# import psycopg2
import pandas as pd
import sqlalchemy as salc
import numpy as np
import warnings
import datetime
import json
# from scipy import stats
from flask import request, send_file, Response
import math

from bokeh.palettes import Colorblind, mpl, Category20
from bokeh.layouts import gridplot, column
from bokeh.models.annotations import Title
from bokeh.io import export_png, show   # get_screenshot_as_png
# from bokeh.io.export import get_screenshot_as_png
from bokeh.embed import json_item
from bokeh.models import ColumnDataSource, Legend, LabelSet, Range1d, Label, FactorRange, BasicTicker, ColorBar, \
    LinearColorMapper, PrintfTickFormatter
from bokeh.plotting import figure
from bokeh.models.glyphs import Rect
from bokeh.transform import dodge, factor_cmap, transform

warnings.filterwarnings('ignore')


def create_routes(server):
    def pull_request_data_collection(repo_id, start_date, end_date):

        pr_query = salc.sql.text(f"""
                    SELECT
                        repo.repo_id AS repo_id,
                        pull_requests.pr_src_id AS pr_src_id,
                        repo.repo_name AS repo_name,
                        pr_src_author_association,
                        repo_groups.rg_name AS repo_group,
                        pull_requests.pr_src_state,
                        pull_requests.pr_merged_at,
                        pull_requests.pr_created_at AS pr_created_at,
                        pull_requests.pr_closed_at AS pr_closed_at,
                        date_part( 'year', pr_created_at :: DATE ) AS CREATED_YEAR,
                        date_part( 'month', pr_created_at :: DATE ) AS CREATED_MONTH,
                        date_part( 'year', pr_closed_at :: DATE ) AS CLOSED_YEAR,
                        date_part( 'month', pr_closed_at :: DATE ) AS CLOSED_MONTH,
                        pr_src_meta_label,
                        pr_head_or_base,
                        ( EXTRACT ( EPOCH FROM pull_requests.pr_closed_at ) - EXTRACT ( EPOCH FROM pull_requests.pr_created_at ) ) / 3600 AS hours_to_close,
                        ( EXTRACT ( EPOCH FROM pull_requests.pr_closed_at ) - EXTRACT ( EPOCH FROM pull_requests.pr_created_at ) ) / 86400 AS days_to_close, 
                        ( EXTRACT ( EPOCH FROM first_response_time ) - EXTRACT ( EPOCH FROM pull_requests.pr_created_at ) ) / 3600 AS hours_to_first_response,
                        ( EXTRACT ( EPOCH FROM first_response_time ) - EXTRACT ( EPOCH FROM pull_requests.pr_created_at ) ) / 86400 AS days_to_first_response, 
                        ( EXTRACT ( EPOCH FROM last_response_time ) - EXTRACT ( EPOCH FROM pull_requests.pr_created_at ) ) / 3600 AS hours_to_last_response,
                        ( EXTRACT ( EPOCH FROM last_response_time ) - EXTRACT ( EPOCH FROM pull_requests.pr_created_at ) ) / 86400 AS days_to_last_response, 
                        first_response_time,
                        last_response_time,
                        average_time_between_responses,
                        assigned_count,
                        review_requested_count,
                        labeled_count,
                        subscribed_count,
                        mentioned_count,
                        referenced_count,
                        closed_count,
                        head_ref_force_pushed_count,
                        merged_count,
                        milestoned_count,
                        unlabeled_count,
                        head_ref_deleted_count,
                        comment_count,
                        lines_added, 
                        lines_removed,
                        commit_count, 
                        file_count
                    FROM
                        repo,
                        repo_groups,
                        pull_requests LEFT OUTER JOIN ( 
                            SELECT pull_requests.pull_request_id,
                            count(*) FILTER (WHERE action = 'assigned') AS assigned_count,
                            count(*) FILTER (WHERE action = 'review_requested') AS review_requested_count,
                            count(*) FILTER (WHERE action = 'labeled') AS labeled_count,
                            count(*) FILTER (WHERE action = 'unlabeled') AS unlabeled_count,
                            count(*) FILTER (WHERE action = 'subscribed') AS subscribed_count,
                            count(*) FILTER (WHERE action = 'mentioned') AS mentioned_count,
                            count(*) FILTER (WHERE action = 'referenced') AS referenced_count,
                            count(*) FILTER (WHERE action = 'closed') AS closed_count,
                            count(*) FILTER (WHERE action = 'head_ref_force_pushed') AS head_ref_force_pushed_count,
                            count(*) FILTER (WHERE action = 'head_ref_deleted') AS head_ref_deleted_count,
                            count(*) FILTER (WHERE action = 'milestoned') AS milestoned_count,
                            count(*) FILTER (WHERE action = 'merged') AS merged_count,
                            MIN(message.msg_timestamp) AS first_response_time,
                            COUNT(DISTINCT message.msg_timestamp) AS comment_count,
                            MAX(message.msg_timestamp) AS last_response_time,
                            (MAX(message.msg_timestamp) - MIN(message.msg_timestamp)) / COUNT(DISTINCT message.msg_timestamp) AS average_time_between_responses
                            FROM pull_request_events, pull_requests, repo, pull_request_message_ref, message
                            WHERE repo.repo_id = {repo_id}
                            AND repo.repo_id = pull_requests.repo_id
                            AND pull_requests.pull_request_id = pull_request_events.pull_request_id
                            AND pull_requests.pull_request_id = pull_request_message_ref.pull_request_id
                            AND pull_request_message_ref.msg_id = message.msg_id
                            GROUP BY pull_requests.pull_request_id
                        ) response_times
                        ON pull_requests.pull_request_id = response_times.pull_request_id
                        LEFT OUTER JOIN (
                            SELECT pull_request_commits.pull_request_id, count(DISTINCT pr_cmt_sha) AS commit_count                                FROM pull_request_commits, pull_requests, pull_request_meta
                            WHERE pull_requests.pull_request_id = pull_request_commits.pull_request_id
                            AND pull_requests.pull_request_id = pull_request_meta.pull_request_id
                            AND pull_requests.repo_id = {repo_id}
                            AND pr_cmt_sha <> pull_requests.pr_merge_commit_sha
                            AND pr_cmt_sha <> pull_request_meta.pr_sha
                            GROUP BY pull_request_commits.pull_request_id
                        ) all_commit_counts
                        ON pull_requests.pull_request_id = all_commit_counts.pull_request_id
                        LEFT OUTER JOIN (
                            SELECT MAX(pr_repo_meta_id), pull_request_meta.pull_request_id, pr_head_or_base, pr_src_meta_label
                            FROM pull_requests, pull_request_meta
                            WHERE pull_requests.pull_request_id = pull_request_meta.pull_request_id
                            AND pull_requests.repo_id = {repo_id}
                            AND pr_head_or_base = 'base'
                            GROUP BY pull_request_meta.pull_request_id, pr_head_or_base, pr_src_meta_label
                        ) base_labels
                        ON base_labels.pull_request_id = all_commit_counts.pull_request_id
                        LEFT OUTER JOIN (
                            SELECT sum(cmt_added) AS lines_added, sum(cmt_removed) AS lines_removed, pull_request_commits.pull_request_id, count(DISTINCT cmt_filename) AS file_count
                            FROM pull_request_commits, commits, pull_requests, pull_request_meta
                            WHERE cmt_commit_hash = pr_cmt_sha
                            AND pull_requests.pull_request_id = pull_request_commits.pull_request_id
                            AND pull_requests.pull_request_id = pull_request_meta.pull_request_id
                            AND pull_requests.repo_id = {repo_id}
                            AND commits.repo_id = pull_requests.repo_id
                            AND commits.cmt_commit_hash <> pull_requests.pr_merge_commit_sha
                            AND commits.cmt_commit_hash <> pull_request_meta.pr_sha
                            GROUP BY pull_request_commits.pull_request_id
                        ) master_merged_counts 
                        ON base_labels.pull_request_id = master_merged_counts.pull_request_id                    
                    WHERE 
                        repo.repo_group_id = repo_groups.repo_group_id 
                        AND repo.repo_id = pull_requests.repo_id 
                        AND repo.repo_id = {repo_id} 
                    ORDER BY
                       merged_count DESC
                        """)
        pr_all = pd.read_sql(pr_query, server.augur_app.database)

        pr_all[['assigned_count',
                'review_requested_count',
                'labeled_count',
                'subscribed_count',
                'mentioned_count',
                'referenced_count',
                'closed_count',
                'head_ref_force_pushed_count',
                'merged_count',
                'milestoned_count',
                'unlabeled_count',
                'head_ref_deleted_count',
                'comment_count',
                'commit_count',
                'file_count',
                'lines_added',
                'lines_removed'
                ]] = pr_all[['assigned_count',
                             'review_requested_count',
                             'labeled_count',
                             'subscribed_count',
                             'mentioned_count',
                             'referenced_count',
                             'closed_count',
                             'head_ref_force_pushed_count',
                             'merged_count',
                             'milestoned_count',
                             'unlabeled_count',
                             'head_ref_deleted_count',
                             'comment_count',
                             'commit_count',
                             'file_count',
                             'lines_added',
                             'lines_removed'
                             ]].astype(float)
        # Change years to int so that doesn't display as 2019.0 for example
        pr_all[['created_year', 'closed_year']] = pr_all[['created_year', 'closed_year']].fillna(-1).astype(int).astype(
            str)

        start_date = pd.to_datetime(start_date)
        # end_date = pd.to_datetime('2020-02-01 09:00:00')
        end_date = pd.to_datetime(end_date)
        pr_all = pr_all[(pr_all['pr_created_at'] > start_date) & (pr_all['pr_closed_at'] < end_date)]

        pr_all['created_year'] = pr_all['created_year'].map(int)
        pr_all['created_month'] = pr_all['created_month'].map(int)
        pr_all['created_month'] = pr_all['created_month'].map(lambda x: '{0:0>2}'.format(x))
        pr_all['created_yearmonth'] = pd.to_datetime(
            pr_all['created_year'].map(str) + '-' + pr_all['created_month'].map(str) + '-01')

        # getting the number of days of (today - created at) for the PRs that are still open
        # and putting this in the days_to_close column

        # get timedeltas of creation time to todays date/time
        days_to_close_open_pr = datetime.datetime.now() - pr_all.loc[pr_all['pr_src_state'] == 'open']['pr_created_at']

        # get num days from above timedelta
        days_to_close_open_pr = days_to_close_open_pr.apply(lambda x: x.days).astype(int)

        # for only OPEN pr's, set the days_to_close column equal to above dataframe
        pr_all.loc[pr_all['pr_src_state'] == 'open'] = pr_all.loc[pr_all['pr_src_state'] == 'open'].assign(
            days_to_close=days_to_close_open_pr)

        pr_all.loc[pr_all['pr_src_state'] == 'open'].head()

        # initiate column by setting all null datetimes
        pr_all['closed_yearmonth'] = pd.to_datetime(np.nan)

        # Fill column with prettified string of year/month closed that looks like: 2019-07-01
        pr_all.loc[pr_all['pr_src_state'] == 'closed'] = pr_all.loc[pr_all['pr_src_state'] == 'closed'].assign(
            closed_yearmonth=pd.to_datetime(pr_all.loc[pr_all['pr_src_state'] == 'closed']['closed_year'].astype(int
                                                                                                                 ).map(
                str) + '-' + pr_all.loc[pr_all['pr_src_state'] == 'closed']['closed_month'].astype(int).map(
                str) + '-01'))

        """ Merged flag """
        if 'pr_merged_at' in pr_all.columns.values:
            pr_all['pr_merged_at'] = pr_all['pr_merged_at'].fillna(0)
            pr_all['merged_flag'] = 'Not Merged / Rejected'
            pr_all['merged_flag'].loc[pr_all['pr_merged_at'] != 0] = 'Merged / Accepted'
            pr_all['merged_flag'].loc[pr_all['pr_src_state'] == 'open'] = 'Still Open'
            del pr_all['pr_merged_at']

        # Isolate the different state PRs for now
        pr_open = pr_all.loc[pr_all['pr_src_state'] == 'open']
        pr_closed = pr_all.loc[pr_all['pr_src_state'] == 'closed']
        pr_merged = pr_all.loc[pr_all['merged_flag'] == 'Merged / Accepted']
        pr_not_merged = pr_all.loc[pr_all['merged_flag'] == 'Not Merged / Rejected']

        # Filtering the 80th percentile slowest PRs
        def filter_20_per_slowest(input_df):
            pr_slow20_filtered = pd.DataFrame()
            pr_slow20_x = pd.DataFrame()
            pr_slow20_filtered = input_df.copy()
            pr_slow20_filtered['percentile_rank_local'] = pr_slow20_filtered.days_to_close.rank(pct=True)
            pr_slow20_filtered = pr_slow20_filtered.query('percentile_rank_local >= .8', )

            return pr_slow20_filtered

        pr_slow20_open = filter_20_per_slowest(pr_open)
        pr_slow20_closed = filter_20_per_slowest(pr_closed)
        pr_slow20_merged = filter_20_per_slowest(pr_merged)
        pr_slow20_not_merged = filter_20_per_slowest(pr_not_merged)
        pr_slow20_all = filter_20_per_slowest(pr_all)

        return pr_all, pr_open, pr_closed, pr_merged, pr_not_merged, pr_slow20_all, pr_slow20_open, pr_slow20_closed, pr_slow20_merged, pr_slow20_not_merged

    def remove_outliers(input_df, field, num_outliers_repo_map):
        df_no_outliers = input_df.copy()
        for repo_name, num_outliers in num_outliers_repo_map.items():
            indices_to_drop = input_df.loc[input_df['repo_name'] == repo_name].nlargest(num_outliers, field).index
            df_no_outliers = df_no_outliers.drop(index=indices_to_drop)
        return df_no_outliers

    def remove_outliers_by_standard_deviation(input_df, column):
        '''Takes a dataframe and a numeric column name.
        Then removes all rows thare are than 3 standard deviations from the mean.
        Returns a df without outliers, the # of outliers removed, outlier cutoff value'''

        # finds rows that are more than 3 standard deviations from the mean
        outlier_cutoff = input_df[column].mean() + (3 * input_df[column].std())
        outlier_mask = input_df[column] > outlier_cutoff

        # determine number of outliers
        outliers_removed = len(input_df.loc[outlier_mask])

        df_no_outliers = input_df.loc[~outlier_mask]

        return df_no_outliers, outliers_removed, outlier_cutoff

    def hex_to_RGB(hex):
        ''' "#FFFFFF" -> [255,255,255] '''
        # Pass 16 to the integer function for change of base
        return [int(hex[i:i + 2], 16) for i in range(1, 6, 2)]

    def color_dict(gradient):
        ''' Takes in a list of RGB sub-lists and returns dictionary of
        colors in RGB and hex form for use in a graphing function
        defined later on '''
        return {"hex": [RGB_to_hex(RGB) for RGB in gradient],
                "r": [RGB[0] for RGB in gradient],
                "g": [RGB[1] for RGB in gradient],
                "b": [RGB[2] for RGB in gradient]}

    def RGB_to_hex(RGB):
        ''' [255,255,255] -> "#FFFFFF" '''
        # Components need to be integers for hex to make sense
        RGB = [int(x) for x in RGB]
        return "#" + "".join(["0{0:x}".format(v) if v < 16 else
                              "{0:x}".format(v) for v in RGB])

    def linear_gradient(start_hex, finish_hex="#FFFFFF", n=10):
        ''' returns a gradient list of (n) colors between
        two hex colors. start_hex and finish_hex
        should be the full six-digit color string,
        inlcuding the number sign ("#FFFFFF") '''
        # Starting and ending colors in RGB form
        s = hex_to_RGB(start_hex)
        f = hex_to_RGB(finish_hex)
        # Initilize a list of the output colors with the starting color
        RGB_list = [s]
        # Calcuate a color at each evenly spaced value of t from 1 to n
        for t in range(1, n):
            # Interpolate RGB vector for color at the current value of t
            curr_vector = [
                int(s[j] + (float(t) / (n - 1)) * (f[j] - s[j]))
                for j in range(3)
            ]
            # Add it to our list of output colors
            RGB_list.append(curr_vector)

        return color_dict(RGB_list)

    # dict of df types, and their locaiton in the tuple that the function pull_request_data_collection returns
    def get_df_tuple_locations():
        return {"pr_all": 0, "pr_open": 1, "pr_closed": 2, "pr_merged": 3, "pr_not_merged": 4, "pr_slow20_all": 5,
                   "pr_slow20_open": 6, "pr_slow20_closed": 7, "pr_slow20_merged": 8, "pr_slow20_not_merged": 9}

    def add_caption_to_plot(caption_plot, caption):

        caption_plot.add_layout(Label(
            x=0,  # Change to shift caption left or right
            y=160,
            x_units='screen',
            y_units='screen',
            text='{}'.format(caption),
            text_font='times',  # Use same font as paper
            text_font_size='15pt',
            render_mode='css'
        ))
        caption_plot.outline_line_color = None

        return caption_plot

    def remove_rows_with_null_values(df, not_null_columns=[]):
        """Remove null data from pandas df

        Parameters
        -- df
            description: the dataframe that will be modified
            type: Pandas Dataframe

        -- list_of_columns
            description: columns that are searched for NULL values
            type: list
            default: [] (means all columns will be checked for NULL values)
            IMPORTANT: if an empty list is passed or nothing is passed it will check all columns for NULL values

        Return Value
            -- Modified Pandas Dataframe
        """

        if len(not_null_columns) == 0:
            not_null_columns = df.columns.to_list()

        total_rows_removed = 0
        for col in not_null_columns:
            rows_removed = len(df.loc[df[col].isnull() == True])

            if rows_removed > 0:
                print(f"{rows_removed} rows have been removed because of null values in column {col}")
                total_rows_removed += rows_removed

            df = df.loc[df[col].isnull() == False]

        if total_rows_removed > 0:
            print(f"\nTotal rows removed because of null data: {total_rows_removed}");
        else:
            print("No null data found")

        return df

    def get_needed_columns(df, list_of_columns):
        """Get only a specific list of columns from a Pandas Dataframe

        Parameters
        -- df
            description: the dataframe that will be modified
            type: Pandas Dataframe

        -- list_of_columns
            description: columns that will be kept in dataframe
            type: list

        Return Value
            -- Modified Pandas Dataframe
        """
        return df[list_of_columns]

    def filter_data(df, needed_columns, not_null_columns=[]):
        """Filters out the unneeded rows in the df, and removed NULL data from df

        Parameters
        -- df
            description: the dataframe that will be modified
            type: Pandas Dataframe

        -- needed_columns
            description: the columns to keep in the dataframe

        -- not_null_columns
            description: columns that will be searched for NULL data,
                         if NULL values are found those rows will be removed
            default: [] (means all columns in needed_columns list will be checked for NULL values)
            IMPORTANT: if an empty list is passed or nothing is passed it will check
                        all columns in needed_columns list for NULL values
        Return Value
            -- Modified Pandas Dataframe
        """

        if all(x in needed_columns for x in not_null_columns):

            df = get_needed_columns(df, needed_columns)
            df = remove_rows_with_null_values(df, not_null_columns)

            return df
        else:
            print("Developer error, not null columns should be a subset of needed columns")
            return df

    def get_repo_id_start_date_and_end_date():

        """ Gets the repo_id, start_date, and end_date from the GET requests array

        :return: repo_id - id of the repo data is being retrieved for
        :return: start_date - earliest time on visualization. Defaults to the January 1st of last year
        :return: end_date - latest time on visualization. Defaults to current date
        """

        now = datetime.datetime.now()

        repo_id = request.args.get('repo_id')
        start_date = str(request.args.get('start_date', "{}-01-01".format(now.year - 1)))
        end_date = str(request.args.get('end_date', "{}-{}-{}".format(now.year, now.month, now.day)))

        if repo_id:

            if start_date < end_date:
                return int(repo_id), start_date, end_date, None
            else:

                error = {
                    "message": "Invalid end_date. end_date is before the start_date",
                    "status_code": 400
                }

                return int(repo_id), None, None, error

        else:
            error = {
                "message": "repo_id not specified. Use this endpoint to get a list of available repos: http://<your_host>/api/unstable/repos",
                "status_code": 400
            }
            return None, None, None, error

    @server.app.route('/{}/pull_request_reports/average_commits_per_PR/'.format(server.api_version), methods=["GET"])
    def average_commits_per_PR():

        repo_id, start_date, end_date, error = get_repo_id_start_date_and_end_date()

        if error:
            return Response(response=error["message"],
                            mimetype='application/json',
                            status=error["status_code"])

        group_by = str(request.args.get('group_by', "month"))
        return_json = request.args.get('return_json', "false")

        df_type = get_df_tuple_locations()

        df_tuple = pull_request_data_collection(repo_id=repo_id, start_date=start_date, end_date=end_date)

        y_axis = 'num_commits'
        group_by_bars = 'merged_flag'
        description = 'All'

        # gets pr_all data
        # selects only need columns (pr_closed_needed_columns)
        # removes columns that cannot be NULL (pr_closed_not_null_columns)
        input_df = df_tuple[df_type["pr_all"]]
        needed_columns = ['repo_id', 'repo_name', 'closed_year', 'closed_yearmonth', group_by_bars, 'commit_count']
        input_df = filter_data(input_df, needed_columns)

        if len(input_df) == 0:
            return Response(response="There is no data for this repo, in the database you are accessing",
                            mimetype='application/json',
                            status=200)

        # print(input_df.to_string())

        repo_dict = {repo_id: input_df.loc[input_df['repo_id'] == repo_id].iloc[0]['repo_name']}

        driver_df = input_df.copy()  # deep copy input data so we do not change the external dataframe

        # Change closed year to int so that doesn't display as 2019.0 for example
        driver_df['closed_year'] = driver_df['closed_year'].astype(int).astype(str)

        # defaults to year
        x_axis = 'closed_year'
        x_groups = sorted(list(driver_df[x_axis].unique()))

        if group_by == 'month':
            x_axis = "closed_yearmonth"
            x_groups = np.unique(np.datetime_as_string(input_df[x_axis], unit='M'))

        # inner groups on x_axis they are merged and not_merged
        groups = list(driver_df[group_by_bars].unique())

        # setup color pallete
        try:
            colors = mpl['Plasma'][len(groups)]
        except:
            colors = [mpl['Plasma'][3][0]] + [mpl['Plasma'][3][1]]

        merged_avg_values = list(driver_df.loc[driver_df[group_by_bars] == 'Merged / Accepted'].groupby([x_axis],
                                                                                                        as_index=False).mean().round(
            1)['commit_count'])
        not_merged_avg_values = list(
            driver_df.loc[driver_df[group_by_bars] == 'Not Merged / Rejected'].groupby([x_axis],
                                                                                       as_index=False).mean().round(1)[
                'commit_count'])

        # Setup data in format for grouped bar chart
        data = {
            'years': x_groups,
            'Merged / Accepted': merged_avg_values,
            'Not Merged / Rejected': not_merged_avg_values,
        }

        x = [(year, pr_state) for year in x_groups for pr_state in groups]
        counts = sum(zip(data['Merged / Accepted'], data['Not Merged / Rejected']), ())

        source = ColumnDataSource(data=dict(x=x, counts=counts))

        title_beginning = '{}: '.format(repo_dict[repo_id])
        title = "{}Average Commit Counts Per Year for {} Pull Requests".format(title_beginning, description)

        plot_width = len(x_groups) * 300
        title_text_font_size = 16

        if (len(title) * title_text_font_size / 2) > plot_width:
            plot_width = int(len(title) * title_text_font_size / 2) + 40

        p = figure(x_range=FactorRange(*x), plot_height=450, plot_width=plot_width, title=title,
                   y_range=(0, max(merged_avg_values + not_merged_avg_values) * 1.15), toolbar_location=None)

        # Vertical bar glyph
        p.vbar(x='x', top='counts', width=0.9, source=source, line_color="white",
               fill_color=factor_cmap('x', palette=colors, factors=groups, start=1, end=2))

        # Data label 
        labels = LabelSet(x='x', y='counts', text='counts',  # y_offset=-8, x_offset=34,
                          text_font_size="12pt", text_color="black",
                          source=source, text_align='center')
        p.add_layout(labels)

        p.y_range.start = 0
        p.x_range.range_padding = 0.1
        p.xaxis.major_label_orientation = 1
        p.xgrid.grid_line_color = None

        p.yaxis.axis_label = 'Average Commits / Pull Request'
        p.xaxis.axis_label = 'Year Closed'

        p.title.align = "center"
        p.title.text_font_size = "{}px".format(title_text_font_size)

        p.xaxis.axis_label_text_font_size = "16px"
        p.xaxis.major_label_text_font_size = "15px"

        p.yaxis.axis_label_text_font_size = "15px"
        p.yaxis.major_label_text_font_size = "15px"

        plot = p

        p = figure(width=plot_width, height=200, margin=(0, 0, 0, 0))
        caption = "This graph shows the average commits per pull requests over an entire year," \
                  " for merged and not merged pull requests."
        p = add_caption_to_plot(p, caption)

        caption_plot = p

        grid = gridplot([[plot], [caption_plot]])

        if return_json == "true":
            var = Response(response=json.dumps(json_item(grid, "average_commits_per_PR")),
                           mimetype='application/json',
                           status=200)

            var.headers["Access-Control-Allow-Orgin"] = "*"

            return var

            # opts = FirefoxOptions()
        # opts.add_argument("--headless")
        # driver = webdriver.Firefox(firefox_options=opts)
        filename = export_png(grid, timeout=180)

        return send_file(filename)

    @server.app.route('/{}/pull_request_reports/average_comments_per_PR/'.format(server.api_version), methods=["GET"])
    def average_comments_per_PR():

        repo_id, start_date, end_date, error = get_repo_id_start_date_and_end_date()

        if error:
            return Response(response=error["message"],
                            mimetype='application/json',
                            status=error["status_code"])

        return_json = request.args.get('return_json', "false")

        df_type = get_df_tuple_locations()

        df_tuple = pull_request_data_collection(repo_id=repo_id, start_date=start_date, end_date=end_date)

        group_by = 'merged_flag'
        x_axis = 'comment_count'
        description = "All Closed"
        y_axis = 'closed_year'

        # gets pr_closed data
        # selects only need columns (pr_closed_needed_columns)
        # removes columns that cannot be NULL (pr_closed_not_null_columns)
        input_df = df_tuple[df_type["pr_closed"]]
        needed_columns = ['repo_id', 'repo_name', y_axis, group_by, x_axis]
        not_null_columns = needed_columns
        input_df = filter_data(input_df, needed_columns)

        if len(input_df) == 0:
            return Response(response="There is no data for this repo, in the database you are accessing",
                            mimetype='application/json',
                            status=200)

        repo_dict = {repo_id: input_df.loc[input_df['repo_id'] == repo_id].iloc[0]['repo_name']}

        driver_df = input_df.copy()

        try:
            y_groups = sorted(list(driver_df[y_axis].unique()))
        except:
            y_groups = [repo_id]

        groups = driver_df[group_by].unique()
        try:
            colors = mpl['Plasma'][len(groups)]
        except:
            colors = [mpl['Plasma'][3][0]] + [mpl['Plasma'][3][1]]

        len_not_merged = len(driver_df.loc[driver_df['merged_flag'] == 'Not Merged / Rejected'])
        len_merged = len(driver_df.loc[driver_df['merged_flag'] == 'Merged / Accepted'])

        title_beginning = '{}: '.format(repo_dict[repo_id])
        plot_width = 650
        p = figure(y_range=y_groups, plot_height=450, plot_width=plot_width,
                   # y_range=y_groups,#(pr_all[y_axis].min(),pr_all[y_axis].max()) #y_axis_type="datetime",
                   title='{} {}'.format(title_beginning, "Mean Comments for {} Pull Requests".format(description)),
                   toolbar_location=None)

        possible_maximums = []
        for y_value in y_groups:

            y_merged_data = driver_df.loc[
                (driver_df[y_axis] == y_value) & (driver_df['merged_flag'] == 'Merged / Accepted')]
            y_not_merged_data = driver_df.loc[
                (driver_df[y_axis] == y_value) & (driver_df['merged_flag'] == 'Not Merged / Rejected')]

            if len(y_merged_data) > 0:
                y_merged_data_mean = y_merged_data[x_axis].mean()

                if (math.isnan(y_merged_data_mean)):
                    return Response(
                        response="There is no message data for this repo, in the database you are accessing",
                        mimetype='application/json', status=200)
                else:
                    y_merged_data[x_axis + '_mean'] = y_merged_data_mean.round(1)

            else:
                y_merged_data[x_axis + '_mean'] = 0

            if len(y_not_merged_data) > 0:
                y_not_merged_data_mean = y_not_merged_data[x_axis].mean()

                if math.isnan(y_not_merged_data_mean):
                    return Response(
                        response="There is no message data for this repo, in the database you are accessing",
                        mimetype='application/json', status=200)
                else:
                    y_not_merged_data[x_axis + '_mean'] = y_not_merged_data_mean.round(1)

            else:
                y_not_merged_data[x_axis + '_mean'] = 0

            not_merged_source = ColumnDataSource(y_not_merged_data)
            merged_source = ColumnDataSource(y_merged_data)

            possible_maximums.append(max(y_not_merged_data[x_axis + '_mean']))
            possible_maximums.append(max(y_merged_data[x_axis + '_mean']))

            # mean comment count for merged
            merged_comment_count_glyph = p.hbar(y=dodge(y_axis, -0.1, range=p.y_range), left=0, right=x_axis + '_mean',
                                                height=0.04 * len(driver_df[y_axis].unique()),
                                                source=merged_source,
                                                fill_color="black")  # ,legend_label="Mean Days to Close",
            # Data label 
            labels = LabelSet(x=x_axis + '_mean', y=dodge(y_axis, -0.1, range=p.y_range), text=x_axis + '_mean',
                              y_offset=-8, x_offset=34,
                              text_font_size="12pt", text_color="black",
                              source=merged_source, text_align='center')
            p.add_layout(labels)
            # mean comment count For nonmerged
            not_merged_comment_count_glyph = p.hbar(y=dodge(y_axis, 0.1, range=p.y_range), left=0,
                                                    right=x_axis + '_mean',
                                                    height=0.04 * len(driver_df[y_axis].unique()),
                                                    source=not_merged_source,
                                                    fill_color="#e84d60")  # legend_label="Mean Days to Close",
            # Data label 
            labels = LabelSet(x=x_axis + '_mean', y=dodge(y_axis, 0.1, range=p.y_range), text=x_axis + '_mean',
                              y_offset=-8, x_offset=34,
                              text_font_size="12pt", text_color="#e84d60",
                              source=not_merged_source, text_align='center')
            p.add_layout(labels)

        #         p.y_range.range_padding = 0.1
        p.ygrid.grid_line_color = None
        p.legend.location = "bottom_right"
        p.axis.minor_tick_line_color = None
        p.outline_line_color = None
        p.xaxis.axis_label = 'Average Comments / Pull Request'
        p.yaxis.axis_label = 'Repository' if y_axis == 'repo_name' else 'Year Closed' if y_axis == 'closed_year' else ''

        legend = Legend(
            items=[
                ("Merged Pull Request Mean Comment Count", [merged_comment_count_glyph]),
                ("Rejected Pull Request Mean Comment Count", [not_merged_comment_count_glyph])
            ],

            location='center',
            orientation='vertical',
            border_line_color="black"
        )
        p.add_layout(legend, "below")

        p.title.text_font_size = "16px"
        p.title.align = "center"

        p.xaxis.axis_label_text_font_size = "16px"
        p.xaxis.major_label_text_font_size = "16px"

        p.yaxis.axis_label_text_font_size = "16px"
        p.yaxis.major_label_text_font_size = "16px"

        p.x_range = Range1d(0, max(possible_maximums) * 1.15)

        plot = p

        p = figure(width=plot_width, height=200, margin=(0, 0, 0, 0))
        caption = "This graph shows the average number of comments per merged or not merged pull request."

        p = add_caption_to_plot(p, caption)

        caption_plot = p

        grid = gridplot([[plot], [caption_plot]])

        if return_json == "true":
            var = Response(response=json.dumps(json_item(grid, "average_comments_per_PR")),
                           mimetype='application/json',
                           status=200)

            var.headers["Access-Control-Allow-Orgin"] = "*"

            return var

            # opts = FirefoxOptions()
        # opts.add_argument("--headless")
        # driver = webdriver.Firefox(firefox_options=opts)
        filename = export_png(grid, timeout=180)

        return send_file(filename)

    @server.app.route('/{}/pull_request_reports/PR_counts_by_merged_status/'.format(server.api_version),
                      methods=["GET"])
    def PR_counts_by_merged_status():

        repo_id, start_date, end_date, error = get_repo_id_start_date_and_end_date()

        if error:
            return Response(response=error["message"],
                            mimetype='application/json',
                            status=error["status_code"])

        return_json = request.args.get('return_json', "false")

        x_axis = 'closed_year'
        description = 'All Closed'

        df_type = get_df_tuple_locations()

        df_tuple = pull_request_data_collection(repo_id=repo_id, start_date=start_date, end_date=end_date)

        # gets pr_closed data
        # selects only need columns (pr_closed_needed_columns)
        # removes columns that cannot be NULL (pr_closed_not_null_columns)
        pr_closed = df_tuple[df_type["pr_closed"]]
        pr_closed_needed_columns = ['repo_id', 'repo_name', x_axis, 'merged_flag']
        pr_closed = filter_data(pr_closed, pr_closed_needed_columns)

        # gets pr_slow20_not_merged data
        # selects only need columns (pr_slow20_not_merged_needed_columns)
        # removes columns that cannot be NULL (pr_slow20_not_merged_not_null_columns)
        pr_slow20_not_merged = df_tuple[df_type["pr_slow20_not_merged"]]
        pr_slow20_not_merged_needed_columns = ['repo_id', 'repo_name', x_axis, 'merged_flag']
        pr_slow20_not_merged = filter_data(pr_slow20_not_merged, pr_slow20_not_merged_needed_columns,)

        # gets pr_slow20_merged data
        # selects only need columns (pr_slow20_not_merged_needed_columns)
        # removes columns that cannot be NULL (pr_slow20_not_merged_not_null_columns)
        pr_slow20_merged = df_tuple[df_type["pr_slow20_merged"]]
        pr_slow20_merged_needed_columns = ['repo_id', 'repo_name', x_axis, 'merged_flag']
        pr_slow20_merged = filter_data(pr_slow20_merged, pr_slow20_merged_needed_columns)

        if len(pr_closed) == 0 or len(pr_slow20_not_merged) == 0 or len(pr_slow20_merged) == 0:
            return Response(response="There is no data for this repo, in the database you are accessing",
                            mimetype='application/json',
                            status=200)

        repo_dict = {repo_id: pr_closed.loc[pr_closed['repo_id'] == repo_id].iloc[0]['repo_name']}

        data_dict = {'All': pr_closed, 'Slowest 20%': pr_slow20_not_merged.append(pr_slow20_merged, ignore_index=True)}

        colors = mpl['Plasma'][6]

        for data_desc, input_df in data_dict.items():
            x_groups = sorted(list(input_df[x_axis].astype(str).unique()))
            break

        plot_width = 315 * len(x_groups)

        if plot_width < 900:
            plot_width = 900
        title_beginning = repo_dict[repo_id]
        p = figure(x_range=x_groups, plot_height=350, plot_width=plot_width,
                   title='{}: {}'.format(title_beginning,
                                         "Count of {} Pull Requests by Merged Status".format(description)),
                   toolbar_location=None)

        dodge_amount = 0.12
        color_index = 0
        x_offset = 60

        all_totals = []
        for data_desc, input_df in data_dict.items():
            driver_df = input_df.copy()

            driver_df[x_axis] = driver_df[x_axis].astype(str)

            groups = sorted(list(driver_df['merged_flag'].unique()))

            driver_df = driver_df.loc[driver_df['repo_id'] == repo_id]

            len_merged = []
            zeros = []
            len_not_merged = []
            totals = []

            for x_group in x_groups:
                len_merged_entry = len(
                    driver_df.loc[(driver_df['merged_flag'] == 'Merged / Accepted') & (driver_df[x_axis] == x_group)])
                totals += [len(driver_df.loc[(driver_df['merged_flag'] == 'Not Merged / Rejected') & (
                            driver_df[x_axis] == x_group)]) + len_merged_entry]
                len_not_merged += [len(driver_df.loc[(driver_df['merged_flag'] == 'Not Merged / Rejected') & (
                            driver_df[x_axis] == x_group)])]
                len_merged += [len_merged_entry]
                zeros.append(0)

            data = {'X': x_groups}
            for group in groups:
                data[group] = []
                for x_group in x_groups:
                    data[group] += [
                        len(driver_df.loc[(driver_df['merged_flag'] == group) & (driver_df[x_axis] == x_group)])]

            data['len_merged'] = len_merged
            data['len_not_merged'] = len_not_merged
            data['totals'] = totals
            data['zeros'] = zeros

            if data_desc == "All":
                all_totals = totals

            source = ColumnDataSource(data)

            stacked_bar = p.vbar_stack(groups, x=dodge('X', dodge_amount, range=p.x_range), width=0.2, source=source,
                                       color=colors[1:3], legend_label=[f"{data_desc} " + "%s" % x for x in groups])
            # Data label for merged

            p.add_layout(
                LabelSet(x=dodge('X', dodge_amount, range=p.x_range), y='zeros', text='len_merged', y_offset=2,
                         x_offset=x_offset,
                         text_font_size="12pt", text_color=colors[1:3][0],
                         source=source, text_align='center')
            )
            if min(data['totals']) < 400:
                y_offset = 15
            else:
                y_offset = 0
            # Data label for not merged
            p.add_layout(
                LabelSet(x=dodge('X', dodge_amount, range=p.x_range), y='totals', text='len_not_merged',
                         y_offset=y_offset, x_offset=x_offset,
                         text_font_size="12pt", text_color=colors[1:3][1],
                         source=source, text_align='center')
            )
            # Data label for total
            p.add_layout(
                LabelSet(x=dodge('X', dodge_amount, range=p.x_range), y='totals', text='totals', y_offset=0, x_offset=0,
                         text_font_size="12pt", text_color='black',
                         source=source, text_align='center')
            )
            dodge_amount *= -1
            colors = colors[::-1]
            x_offset *= -1

        p.y_range = Range1d(0, max(all_totals) * 1.4)

        p.xgrid.grid_line_color = None
        p.legend.location = "top_center"
        p.legend.orientation = "horizontal"
        p.axis.minor_tick_line_color = None
        p.outline_line_color = None
        p.yaxis.axis_label = 'Count of Pull Requests'
        p.xaxis.axis_label = 'Repository' if x_axis == 'repo_name' else 'Year Closed' if x_axis == 'closed_year' else ''

        p.title.align = "center"
        p.title.text_font_size = "16px"

        p.xaxis.axis_label_text_font_size = "16px"
        p.xaxis.major_label_text_font_size = "16px"

        p.yaxis.axis_label_text_font_size = "16px"
        p.yaxis.major_label_text_font_size = "16px"

        p.outline_line_color = None

        plot = p

        p = figure(width=plot_width, height=200, margin=(0, 0, 0, 0))
        caption = "This graph shows the number of closed pull requests per year in " \
                  "four different categories. These four categories are All Merged, All Not Merged," \
                  " Slowest 20% Merged, and Slowest 20% Not Merged."
        p = add_caption_to_plot(p, caption)

        caption_plot = p

        grid = gridplot([[plot], [caption_plot]])

        if return_json == "true":
            var = Response(response=json.dumps(json_item(grid, "PR_counts_by_merged_status")),
                           mimetype='application/json',
                           status=200)

            var.headers["Access-Control-Allow-Orgin"] = "*"

            return var

            # opts = FirefoxOptions()
        # opts.add_argument("--headless")
        # driver = webdriver.Firefox(firefox_options=opts)
        filename = export_png(grid, timeout=180)

        return send_file(filename)

    @server.app.route('/{}/pull_request_reports/mean_response_times_for_PR/'.format(server.api_version),
                      methods=["GET"])
    def mean_response_times_for_PR():

        repo_id, start_date, end_date, error = get_repo_id_start_date_and_end_date()

        if error:
            return Response(response=error["message"],
                            mimetype='application/json',
                            status=error["status_code"])

        return_json = request.args.get('return_json', "false")

        df_type = get_df_tuple_locations()

        df_tuple = pull_request_data_collection(repo_id=repo_id, start_date=start_date, end_date=end_date)

        time_unit = 'days'
        x_max = 95
        y_axis = 'closed_year'
        description = "All Closed"
        legend_position = (410, 10)

        # gets pr_closed data
        # selects only need columns (pr_closed_needed_columns)
        # removes columns that cannot be NULL (pr_closed_not_null_columns)
        input_df = df_tuple[df_type["pr_closed"]]
        needed_columns = ['repo_id', 'repo_name', y_axis, 'merged_flag', time_unit + '_to_first_response',
                          time_unit + '_to_last_response', time_unit + '_to_close']
        input_df = filter_data(input_df, needed_columns)

        if len(input_df) == 0:
            return Response(response="There is no data for this repo, in the database you are accessing",
                            mimetype='application/json',
                            status=200)

        repo_dict = {repo_id: input_df.loc[input_df['repo_id'] == repo_id].iloc[0]['repo_name']}

        driver_df = input_df.copy()  # deep copy input data so we do not alter the external dataframe

        title_beginning = '{}: '.format(repo_dict[repo_id])
        plot_width = 950
        p = figure(toolbar_location=None, y_range=sorted(driver_df[y_axis].unique()), plot_width=plot_width,
                   plot_height=450,  # 75*len(driver_df[y_axis].unique()),
                   title="{}Mean Response Times for Pull Requests {}".format(title_beginning, description))

        first_response_glyphs = []
        last_response_glyphs = []
        merged_days_to_close_glyphs = []
        not_merged_days_to_close_glyphs = []

        possible_maximums = []

        # FIXME repo_set is not defined
        # setup color pallete
        try:
            colors = Colorblind[len(repo_set)]
        except:
            colors = Colorblind[3]

        y_merged_data_list = []
        y_not_merged_data_list = []

        # calculate data frist time to obtain the maximum and make sure there is message data
        for y_value in driver_df[y_axis].unique():

            y_merged_data = driver_df.loc[
                (driver_df[y_axis] == y_value) & (driver_df['merged_flag'] == 'Merged / Accepted')]
            y_not_merged_data = driver_df.loc[
                (driver_df[y_axis] == y_value) & (driver_df['merged_flag'] == 'Not Merged / Rejected')]

            if len(y_merged_data) > 0:

                y_merged_data_first_response_mean = y_merged_data[time_unit + '_to_first_response'].mean()
                y_merged_data_last_response_mean = y_merged_data[time_unit + '_to_last_response'].mean()
                y_merged_data_to_close_mean = y_merged_data[time_unit + '_to_close'].mean()

                if (math.isnan(y_merged_data_first_response_mean) or math.isnan(
                        y_merged_data_last_response_mean) or math.isnan(y_merged_data_to_close_mean)):
                    return Response(
                        response="There is no message data for this repo, in the database you are accessing",
                        mimetype='application/json', status=200)
                else:
                    y_merged_data[time_unit + '_to_first_response_mean'] = y_merged_data_first_response_mean.round(1)
                    y_merged_data[time_unit + '_to_last_response_mean'] = y_merged_data_last_response_mean.round(1)
                    y_merged_data[time_unit + '_to_close_mean'] = y_merged_data_to_close_mean.round(1)
            else:
                y_merged_data[time_unit + '_to_first_response_mean'] = 0.00
                y_merged_data[time_unit + '_to_last_response_mean'] = 0.00
                y_merged_data[time_unit + '_to_close_mean'] = 0.00

            if len(y_not_merged_data) > 0:

                y_not_merged_data_first_response_mean = y_not_merged_data[time_unit + '_to_first_response'].mean()
                y_not_merged_data_last_response_mean = y_not_merged_data[time_unit + '_to_last_response'].mean()
                y_not_merged_data_to_close_mean = y_not_merged_data[time_unit + '_to_close'].mean()

                if (math.isnan(y_not_merged_data_first_response_mean) or math.isnan(
                        y_not_merged_data_last_response_mean) or math.isnan(y_not_merged_data_to_close_mean)):
                    return Response(
                        response="There is no message data for this repo, in the database you are accessing",
                        mimetype='application/json', status=200)
                else:
                    y_not_merged_data[
                        time_unit + '_to_first_response_mean'] = y_not_merged_data_first_response_mean.round(1)
                    y_not_merged_data[
                        time_unit + '_to_last_response_mean'] = y_not_merged_data_last_response_mean.round(1)
                    y_not_merged_data[time_unit + '_to_close_mean'] = y_not_merged_data_to_close_mean.round(1)
            else:
                y_not_merged_data[time_unit + '_to_first_response_mean'] = 0.00
                y_not_merged_data[time_unit + '_to_last_response_mean'] = 0.00
                y_not_merged_data[time_unit + '_to_close_mean'] = 0.00

            possible_maximums.append(max(y_merged_data[time_unit + '_to_close_mean']))
            possible_maximums.append(max(y_not_merged_data[time_unit + '_to_close_mean']))

            maximum = max(possible_maximums) * 1.15
            ideal_difference = maximum * 0.064

            y_merged_data_list.append(y_merged_data)
            y_not_merged_data_list.append(y_not_merged_data)

        # loop through data and add it to the plot
        for index in range(0, len(y_merged_data_list)):

            y_merged_data = y_merged_data_list[index]
            y_not_merged_data = y_not_merged_data_list[index]

            not_merged_source = ColumnDataSource(y_not_merged_data)
            merged_source = ColumnDataSource(y_merged_data)

            # mean PR length for merged
            merged_days_to_close_glyph = p.hbar(y=dodge(y_axis, -0.1, range=p.y_range), left=0,
                                                right=time_unit + '_to_close_mean',
                                                height=0.04 * len(driver_df[y_axis].unique()),
                                                source=merged_source,
                                                fill_color="black")  # ,legend_label="Mean Days to Close",
            merged_days_to_close_glyphs.append(merged_days_to_close_glyph)
            # Data label 
            labels = LabelSet(x=time_unit + '_to_close_mean', y=dodge(y_axis, -0.1, range=p.y_range),
                              text=time_unit + '_to_close_mean', y_offset=-8, x_offset=34,  # 34
                              text_font_size="12pt", text_color="black",
                              source=merged_source, text_align='center')
            p.add_layout(labels)

            # mean PR length For nonmerged
            not_merged_days_to_close_glyph = p.hbar(y=dodge(y_axis, 0.1, range=p.y_range), left=0,
                                                    right=time_unit + '_to_close_mean',
                                                    height=0.04 * len(driver_df[y_axis].unique()),
                                                    source=not_merged_source,
                                                    fill_color="#e84d60")  # legend_label="Mean Days to Close",
            not_merged_days_to_close_glyphs.append(not_merged_days_to_close_glyph)
            # Data label 
            labels = LabelSet(x=time_unit + '_to_close_mean', y=dodge(y_axis, 0.1, range=p.y_range),
                              text=time_unit + '_to_close_mean', y_offset=-8, x_offset=44,
                              text_font_size="12pt", text_color="#e84d60",
                              source=not_merged_source, text_align='center')
            p.add_layout(labels)

            # if the difference between two values is less than 6.4 percent move the second one to the right 30 pixels
            if (max(y_merged_data[time_unit + '_to_last_response_mean']) - max(
                    y_merged_data[time_unit + '_to_first_response_mean'])) < ideal_difference:
                merged_x_offset = 30
            else:
                merged_x_offset = 0

            # if the difference between two values is less than 6.4 percent move the second one to the right 30 pixels
            if (max(y_not_merged_data[time_unit + '_to_last_response_mean']) - max(
                    y_not_merged_data[time_unit + '_to_first_response_mean'])) < ideal_difference:
                not_merged_x_offset = 30
            else:
                not_merged_x_offset = 0

            # if there is only one bar set the y_offsets so the labels will not overlap the bars
            if len(driver_df[y_axis].unique()) == 1:
                merged_y_offset = -65
                not_merged_y_offset = 45
            else:
                merged_y_offset = -45
                not_merged_y_offset = 25

            # mean time to first response
            glyph = Rect(x=time_unit + '_to_first_response_mean', y=dodge(y_axis, -0.1, range=p.y_range),
                         width=x_max / 100, height=0.08 * len(driver_df[y_axis].unique()), fill_color=colors[0])
            first_response_glyph = p.add_glyph(merged_source, glyph)
            first_response_glyphs.append(first_response_glyph)
            # Data label 
            labels = LabelSet(x=time_unit + '_to_first_response_mean', y=dodge(y_axis, 0, range=p.y_range),
                              text=time_unit + '_to_first_response_mean', x_offset=0, y_offset=merged_y_offset,  # -60,
                              text_font_size="12pt", text_color=colors[0],
                              source=merged_source, text_align='center')
            p.add_layout(labels)

            # for nonmerged
            glyph = Rect(x=time_unit + '_to_first_response_mean', y=dodge(y_axis, 0.1, range=p.y_range),
                         width=x_max / 100, height=0.08 * len(driver_df[y_axis].unique()), fill_color=colors[0])
            first_response_glyph = p.add_glyph(not_merged_source, glyph)
            first_response_glyphs.append(first_response_glyph)
            # Data label 
            labels = LabelSet(x=time_unit + '_to_first_response_mean', y=dodge(y_axis, 0, range=p.y_range),
                              text=time_unit + '_to_first_response_mean', x_offset=0, y_offset=not_merged_y_offset,
                              # 40,
                              text_font_size="12pt", text_color=colors[0],
                              source=not_merged_source, text_align='center')
            p.add_layout(labels)

            # mean time to last response
            glyph = Rect(x=time_unit + '_to_last_response_mean', y=dodge(y_axis, -0.1, range=p.y_range),
                         width=x_max / 100, height=0.08 * len(driver_df[y_axis].unique()), fill_color=colors[1])
            last_response_glyph = p.add_glyph(merged_source, glyph)
            last_response_glyphs.append(last_response_glyph)
            # Data label 
            labels = LabelSet(x=time_unit + '_to_last_response_mean', y=dodge(y_axis, 0, range=p.y_range),
                              text=time_unit + '_to_last_response_mean', x_offset=merged_x_offset,
                              y_offset=merged_y_offset,  # -60,
                              text_font_size="12pt", text_color=colors[1],
                              source=merged_source, text_align='center')
            p.add_layout(labels)

            # for nonmerged
            glyph = Rect(x=time_unit + '_to_last_response_mean', y=dodge(y_axis, 0.1, range=p.y_range),
                         width=x_max / 100, height=0.08 * len(driver_df[y_axis].unique()), fill_color=colors[1])
            last_response_glyph = p.add_glyph(not_merged_source, glyph)
            last_response_glyphs.append(last_response_glyph)
            # Data label 
            labels = LabelSet(x=time_unit + '_to_last_response_mean', y=dodge(y_axis, 0, range=p.y_range),
                              text=time_unit + '_to_last_response_mean', x_offset=not_merged_x_offset,
                              y_offset=not_merged_y_offset,  # 40,
                              text_font_size="12pt", text_color=colors[1],
                              source=not_merged_source, text_align='center')
            p.add_layout(labels)

        p.title.align = "center"
        p.title.text_font_size = "16px"

        p.xaxis.axis_label = "Days to Close"
        p.xaxis.axis_label_text_font_size = "16px"
        p.xaxis.major_label_text_font_size = "16px"

        # adjust the starting point and ending point based on the maximum of maximum of the graph
        p.x_range = Range1d(maximum / 30 * -1, maximum * 1.15)

        p.yaxis.axis_label = "Repository" if y_axis == 'repo_name' else 'Year Closed' if y_axis == 'closed_year' else ''
        p.yaxis.axis_label_text_font_size = "16px"
        p.yaxis.major_label_text_font_size = "16px"
        p.ygrid.grid_line_color = None
        p.y_range.range_padding = 0.15

        p.outline_line_color = None
        p.toolbar.logo = None
        p.toolbar_location = None

        def add_legend(location, orientation, side):
            legend = Legend(
                items=[
                    ("Mean Days to First Response", first_response_glyphs),
                    ("Mean Days to Last Response", last_response_glyphs),
                    ("Merged Mean Days to Close", merged_days_to_close_glyphs),
                    ("Not Merged Mean Days to Close", not_merged_days_to_close_glyphs)
                ],

                location=location,
                orientation=orientation,
                border_line_color="black"
                #         title='Example Title'
            )
            p.add_layout(legend, side)

        #     add_legend((150, 50), "horizontal", "center")
        add_legend((10, 135), "vertical", "right")

        plot = p

        p = figure(width=plot_width, height=200, margin=(0, 0, 0, 0))
        caption = "This graph shows the average number of days between comments for all closed pull requests per month " \
                  "in four categories. These four categories are All Merged, All Not Merged, Slowest 20% Merged, " \
                  "and Slowest 20% Not Merged."
        p = add_caption_to_plot(p, caption)

        caption_plot = p

        grid = gridplot([[plot], [caption_plot]])

        if return_json == "true":
            var = Response(response=json.dumps(json_item(grid, "mean_response_times_for_PR")),
                           mimetype='application/json',
                           status=200)

            var.headers["Access-Control-Allow-Orgin"] = "*"

            return var

            # opts = FirefoxOptions()
        # opts.add_argument("--headless")
        # driver = webdriver.Firefox(firefox_options=opts)
        filename = export_png(grid, timeout=180)

        return send_file(filename)

    @server.app.route('/{}/pull_request_reports/mean_days_between_PR_comments/'.format(server.api_version),
                      methods=["GET"])
    def mean_days_between_PR_comments():

        repo_id, start_date, end_date, error = get_repo_id_start_date_and_end_date()

        if error:
            return Response(response=error["message"],
                            mimetype='application/json',
                            status=error["status_code"])

        return_json = request.args.get('return_json', "false")

        time_unit = 'Days'
        x_axis = 'closed_yearmonth'
        y_axis = 'average_days_between_responses'
        description = "All Closed"
        line_group = 'merged_flag'
        num_outliers_repo_map = {}

        df_type = get_df_tuple_locations()

        df_tuple = pull_request_data_collection(repo_id=repo_id, start_date=start_date, end_date=end_date)

        # gets pr_closed data
        # selects only need columns (pr_closed_needed_columns)
        # removes columns that cannot be NULL (pr_closed_not_null_columns)
        pr_closed = df_tuple[df_type["pr_closed"]]
        pr_closed_needed_columns = ['repo_id', 'repo_name', x_axis, 'average_time_between_responses', line_group]
        pr_closed = filter_data(pr_closed, pr_closed_needed_columns)

        # gets pr_slow20_not_merged data
        # selects only need columns (pr_slow20_not_merged_needed_columns)
        # removes columns that cannot be NULL (pr_slow20_not_merged_not_null_columns)
        pr_slow20_not_merged = df_tuple[df_type["pr_slow20_not_merged"]]
        pr_slow20_not_merged_needed_columns = ['repo_id', 'repo_name', x_axis, 'average_time_between_responses', line_group]
        pr_slow20_not_merged = filter_data(pr_slow20_not_merged, pr_slow20_not_merged_needed_columns)

        # gets pr_slow20_merged data
        # selects only need columns (pr_slow20_not_merged_needed_columns)
        # removes columns that cannot be NULL (pr_slow20_not_merged_not_null_columns)
        pr_slow20_merged = df_tuple[df_type["pr_slow20_merged"]]
        pr_slow20_merged_needed_columns = ['repo_id', 'repo_name', x_axis, 'average_time_between_responses', line_group]
        pr_slow20_merged = filter_data(pr_slow20_merged, pr_slow20_merged_needed_columns)

        if len(pr_closed) == 0 or len(pr_slow20_not_merged) == 0 or len(pr_slow20_merged) == 0:
            return Response(response="There is no data for this repo, in the database you are accessing",
                            mimetype='application/json',
                            status=200)

        try:
            pr_closed['average_days_between_responses'] = pr_closed['average_time_between_responses'].map(
                lambda x: x.days).astype(float)
            pr_slow20_not_merged['average_days_between_responses'] = pr_slow20_not_merged[
                'average_time_between_responses'].map(lambda x: x.days).astype(float)
            pr_slow20_merged['average_days_between_responses'] = pr_slow20_merged['average_time_between_responses'].map(
                lambda x: x.days).astype(float)
        except:
            return Response(response="There is no message data for this repo, in the database you are accessing",
                            mimetype='application/json',
                            status=200)

        repo_dict = {repo_id: pr_closed.loc[pr_closed['repo_id'] == repo_id].iloc[0]['repo_name']}

        data_dict = {'All': pr_closed, 'Slowest 20%': pr_slow20_not_merged.append(pr_slow20_merged, ignore_index=True)}

        plot_width = 950
        p1 = figure(x_axis_type="datetime",
                    title="{}: Mean {} Between Comments by Month Closed for {} Pull Requests".format(repo_dict[repo_id],
                                                                                                     time_unit,
                                                                                                     description),
                    plot_width=plot_width, x_range=(pr_all[x_axis].min(), pr_all[x_axis].max()), plot_height=500,
                    toolbar_location=None)
        colors = Category20[10][6:]
        color_index = 0

        glyphs = []

        possible_maximums = []
        for data_desc, input_df in data_dict.items():

            driver_df = input_df.copy()

            driver_df = remove_outliers(driver_df, y_axis, num_outliers_repo_map)

            driver_df = driver_df.loc[driver_df['repo_id'] == repo_id]
            index = 0

            driver_df_mean = driver_df.groupby(['repo_id', line_group, x_axis], as_index=False).mean()

            title_ending = ''
            if repo_id:
                title_ending += ' for Repo: {}'.format(repo_id)

            for group_num, line_group_value in enumerate(driver_df[line_group].unique(), color_index):
                glyphs.append(p1.line(driver_df_mean.loc[driver_df_mean[line_group] == line_group_value][x_axis],
                                      driver_df_mean.loc[driver_df_mean[line_group] == line_group_value][y_axis],
                                      color=colors[group_num], line_width=3))
                color_index += 1
                possible_maximums.append(
                    max(driver_df_mean.loc[driver_df_mean[line_group] == line_group_value][y_axis].dropna()))
        for repo, num_outliers in num_outliers_repo_map.items():
            # FIXME repo_name is not defined
            if repo_name == repo:
                p1.add_layout(
                    Title(text="** {} outliers for {} were removed".format(num_outliers, repo), align="center"),
                    "below")

        p1.grid.grid_line_alpha = 0.3
        p1.xaxis.axis_label = 'Month Closed'
        p1.xaxis.ticker.desired_num_ticks = 15
        p1.yaxis.axis_label = 'Mean {} Between Responses'.format(time_unit)
        p1.legend.location = "top_left"

        legend = Legend(
            items=[
                ("All Not Merged / Rejected", [glyphs[0]]),
                ("All Merged / Accepted", [glyphs[1]]),
                ("Slowest 20% Not Merged / Rejected", [glyphs[2]]),
                ("Slowest 20% Merged / Accepted", [glyphs[3]])
            ],

            location='center_right',
            orientation='vertical',
            border_line_color="black"
        )

        p1.add_layout(legend, 'right')

        p1.title.text_font_size = "16px"

        p1.xaxis.axis_label_text_font_size = "16px"
        p1.xaxis.major_label_text_font_size = "16px"

        p1.yaxis.axis_label_text_font_size = "16px"
        p1.yaxis.major_label_text_font_size = "16px"
        p1.xaxis.major_label_orientation = 45.0

        p1.y_range = Range1d(0, max(possible_maximums) * 1.15)

        plot = p1

        p = figure(width=plot_width, height=200, margin=(0, 0, 0, 0))
        caption = "This graph shows the average number of days between comments for all" \
                  " closed pull requests per month in four categories. These four categories" \
                  " are All Merged, All Not Merged, Slowest 20% Merged, and Slowest 20% Not Merged."
        p = add_caption_to_plot(p, caption)

        caption_plot = p

        grid = gridplot([[plot], [caption_plot]])

        if return_json == "true":
            var = Response(response=json.dumps(json_item(grid, "mean_days_between_PR_comments")),
                           mimetype='application/json',
                           status=200)

            var.headers["Access-Control-Allow-Orgin"] = "*"

            return var

            # opts = FirefoxOptions()
        # opts.add_argument("--headless")
        # driver = webdriver.Firefox(firefox_options=opts)
        filename = export_png(grid, timeout=180)

        return send_file(filename)

    @server.app.route('/{}/pull_request_reports/PR_time_to_first_response/'.format(server.api_version), methods=["GET"])
    def PR_time_to_first_response():

        repo_id, start_date, end_date, error = get_repo_id_start_date_and_end_date()

        if error:
            return Response(response=error["message"],
                            mimetype='application/json',
                            status=error["status_code"])

        return_json = request.args.get('return_json', "false")
        remove_outliers = str(request.args.get('remove_outliers', "true"))

        x_axis = 'pr_closed_at'
        y_axis = 'days_to_first_response'
        description = 'All'
        group_by = 'merged_flag'
        legend_position = 'top_right'

        df_type = get_df_tuple_locations()

        df_tuple = pull_request_data_collection(repo_id=repo_id, start_date=start_date, end_date=end_date)

        pr_closed = df_tuple[df_type["pr_closed"]]
        needed_columns = ['repo_id', 'repo_name', x_axis, group_by, y_axis]
        pr_closed = filter_data(pr_closed, needed_columns)

        if len(pr_closed) == 0:
            return Response(response="There is no data for this repo, in the database you are accessing",
                            mimetype='application/json',
                            status=200)

        repo_dict = {repo_id: pr_closed.loc[pr_closed['repo_id'] == repo_id].iloc[0]['repo_name']}

        driver_df = pr_closed.copy()

        outliers_removed = 0

        if remove_outliers == "true":
            driver_df, outliers_removed, outlier_cutoff = remove_outliers_by_standard_deviation(driver_df, 'days_to_first_response')

        group_by_groups = sorted(driver_df[group_by].unique())

        # setup color pallete
        try:
            # FIXME repo_set is not defined
            colors = Colorblind[len(repo_set)]
        except:
            colors = Colorblind[3]

        title_beginning = '{}: '.format(repo_dict[repo_id])
        plot_width = 180 * 5
        p = figure(x_range=(
        driver_df[x_axis].min() - datetime.timedelta(days=30), driver_df[x_axis].max() + datetime.timedelta(days=25)),
                   # (driver_df[y_axis].min(), driver_df[y_axis].max()),
                   toolbar_location=None,
                   title='{}Days to First Response for {} Closed Pull Requests'.format(title_beginning, description),
                   plot_width=plot_width,
                   plot_height=400, x_axis_type='datetime')

        for index, group_by_group in enumerate(group_by_groups):
            p.scatter(x_axis, y_axis, color=colors[index], marker="square",
                      source=driver_df.loc[driver_df[group_by] == group_by_group], legend_label=group_by_group)

            if group_by_group == "Merged / Accepted":
                merged_values = driver_df.loc[driver_df[group_by] == group_by_group][y_axis].dropna().values.tolist()
            else:
                not_merged_values = driver_df.loc[driver_df[group_by] == group_by_group][
                    y_axis].dropna().values.tolist()

        values = not_merged_values + merged_values

        if outliers_removed > 0:
            if repo_id:
                p.add_layout(Title(
                    text="** Outliers cut off at {} days: {} outlier(s) for {} were removed **".format(outlier_cutoff,
                                                                                                       outliers_removed,
                                                                                                       repo_dict[
                                                                                                           repo_id]),
                    align="center"), "below")
            else:
                p.add_layout(Title(
                    text="** Outliers cut off at {} days: {} outlier(s) were removed **".format(outlier_cutoff,
                                                                                                outliers_removed),
                    align="center"), "below")

        p.xaxis.axis_label = 'Date Closed' if x_axis == 'pr_closed_at' else 'Date Created' if x_axis == 'pr_created_at' else 'Date'
        p.yaxis.axis_label = 'Days to First Response'
        p.legend.location = legend_position

        p.title.align = "center"
        p.title.text_font_size = "16px"

        p.xaxis.axis_label_text_font_size = "16px"
        p.xaxis.major_label_text_font_size = "16px"

        p.yaxis.axis_label_text_font_size = "16px"
        p.yaxis.major_label_text_font_size = "16px"

        if len(values) == 0:
            return Response(response="There is no message data for this repo, in the database you are accessing",
                            mimetype='application/json',
                            status=200)

        # determine y_max by finding the max of the values and scaling it up a small amoutn
        y_max = max(values) * 1.015

        p.y_range = Range1d(0, y_max)

        plot = p

        p = figure(width=plot_width, height=200, margin=(0, 0, 0, 0))
        caption = "This graph shows the days to first reponse for individual pull requests, either Merged or Not Merged."
        p = add_caption_to_plot(p, caption)

        caption_plot = p

        grid = gridplot([[plot], [caption_plot]])

        if return_json == "true":
            var = Response(response=json.dumps(json_item(grid, "PR_time_to_first_response")),
                           mimetype='application/json',
                           status=200)

            var.headers["Access-Control-Allow-Orgin"] = "*"

            return var

            # opts = FirefoxOptions()
        # opts.add_argument("--headless")
        # driver = webdriver.Firefox(firefox_options=opts)
        filename = export_png(grid, timeout=180)

        return send_file(filename)

    @server.app.route('/{}/pull_request_reports/average_PR_events_for_closed_PRs/'.format(server.api_version),
                      methods=["GET"])
    def average_PR_events_for_closed_PRs():

        repo_id, start_date, end_date, error = get_repo_id_start_date_and_end_date()

        if error:
            return Response(response=error["message"],
                            mimetype='application/json',
                            status=error["status_code"])

        return_json = request.args.get('return_json', "false")
        include_comments = str(request.args.get('include_comments', True))

        x_axis = 'closed_year'
        facet = 'merged_flag'
        columns = 2
        x_max = 1100
        y_axis = 'repo_name'
        description = 'All Closed'
        optional_comments = ['comment_count'] if include_comments else []

        df_type = get_df_tuple_locations()

        df_tuple = pull_request_data_collection(repo_id=repo_id, start_date=start_date, end_date=end_date)

        pr_closed = df_tuple[df_type["pr_closed"]]
        needed_columns = ['repo_id', 'repo_name', x_axis, 'assigned_count',
                          'review_requested_count',
                          'labeled_count',
                          'subscribed_count',
                          'mentioned_count',
                          'referenced_count',
                          'closed_count',
                          'head_ref_force_pushed_count',
                          'merged_count',
                          'milestoned_count',
                          'unlabeled_count',
                          'head_ref_deleted_count', facet] + optional_comments
        pr_closed = filter_data(pr_closed, needed_columns)

        if len(pr_closed) == 0:
            return Response(response="There is no data for this repo, in the database you are accessing",
                            mimetype='application/json',
                            status=200)

        repo_dict = {repo_id: pr_closed.loc[pr_closed['repo_id'] == repo_id].iloc[0]['repo_name']}

        colors = linear_gradient('#f5f5dc', '#fff44f', 150)['hex']

        driver_df = pr_closed.copy()
        driver_df[x_axis] = driver_df[x_axis].astype(str)

        if facet == 'closed_year' or y_axis == 'closed_year':
            driver_df['closed_year'] = driver_df['closed_year'].astype(int).astype(str)

        y_groups = [
                       'review_requested_count',
                       'labeled_count',
                       'subscribed_count',
                       'referenced_count',
                       'closed_count',
                       #           'milestoned_count',
                   ] + optional_comments

        optional_group_comments = ['comment'] if include_comments else []
        #     y_groups = ['subscribed', 'mentioned', 'labeled', 'review_requested', 'head_ref_force_pushed',
        #     'referenced', 'closed', 'merged', 'unlabeled', 'head_ref_deleted', 'milestoned', 'assigned']
        #     + optional_group_comments

        x_groups = sorted(list(driver_df[x_axis].unique()))

        grid_array = []
        grid_row = []

        for index, facet_group in enumerate(sorted(driver_df[facet].unique())):

            facet_data = driver_df.loc[driver_df[facet] == facet_group]
            #         display(facet_data.sort_values('merged_count', ascending=False).head(50))
            driver_df_mean = facet_data.groupby(['repo_id', 'repo_name', x_axis], as_index=False).mean().round(1)

            # if a record is field in a record is Nan then it is not counted by count() so when it is not
            # 2 meaning both rows have a value, there is not enough data
            if (driver_df_mean['assigned_count'].count() != 2 or driver_df_mean[
                'review_requested_count'].count() != 2 or driver_df_mean['labeled_count'].count() != 2 or
                    driver_df_mean['subscribed_count'].count() != 2 or driver_df_mean['mentioned_count'].count() != 2 or
                    driver_df_mean['referenced_count'].count() != 2 or
                    driver_df_mean['closed_count'].count() != 2 or driver_df_mean[
                        'head_ref_force_pushed_count'].count() != 2 or driver_df_mean['merged_count'].count() != 2 or
                    driver_df_mean['milestoned_count'].count() != 2 or driver_df_mean['unlabeled_count'].count() != 2 or
                    driver_df_mean['head_ref_deleted_count'].count() != 2 or
                    driver_df_mean['comment_count'].count() != 2):
                return Response(response="There is not enough data for this repo, in the database you are accessing",
                                mimetype='application/json',
                                status=200)

            # print(driver_df_mean.to_string())
            #         data = {'Y' : y_groups}
            #         for group in y_groups:
            #             data[group] = driver_df_mean[group].tolist()
            plot_width = 700
            p = figure(y_range=y_groups, plot_height=500, plot_width=plot_width, x_range=x_groups,
                       title='{}'.format(format(facet_group)))

            for y_group in y_groups:
                driver_df_mean['field'] = y_group
                source = ColumnDataSource(driver_df_mean)
                mapper = LinearColorMapper(palette=colors, low=driver_df_mean[y_group].min(),
                                           high=driver_df_mean[y_group].max())

                p.rect(y='field', x=x_axis, width=1, height=1, source=source,
                       line_color=None, fill_color=transform(y_group, mapper))
                # Data label 
                labels = LabelSet(x=x_axis, y='field', text=y_group, y_offset=-8,
                                  text_font_size="12pt", text_color='black',
                                  source=source, text_align='center')
                p.add_layout(labels)

                color_bar = ColorBar(color_mapper=mapper, location=(0, 0),
                                     ticker=BasicTicker(desired_num_ticks=9),
                                     formatter=PrintfTickFormatter(format="%d"))
            #         p.add_layout(color_bar, 'right')

            p.y_range.range_padding = 0.1
            p.ygrid.grid_line_color = None

            p.legend.location = "bottom_right"
            p.axis.minor_tick_line_color = None
            p.outline_line_color = None

            p.xaxis.axis_label = 'Year Closed'
            p.yaxis.axis_label = 'Event Type'

            p.title.align = "center"
            p.title.text_font_size = "15px"

            p.xaxis.axis_label_text_font_size = "16px"
            p.xaxis.major_label_text_font_size = "16px"

            p.yaxis.axis_label_text_font_size = "16px"
            p.yaxis.major_label_text_font_size = "16px"

            grid_row.append(p)
            if index % columns == columns - 1:
                grid_array.append(grid_row)
                grid_row = []
        grid = gridplot(grid_array)

        # create caption plot
        caption_plot = figure(width=plot_width, height=200, margin=(0, 0, 0, 0))
        caption = "This graph shows the average count of several different event types for " \
                  "closed pull requests per year. It spilits the pull requests into two categories, " \
                  "Merged / Accepted, and Not Merged / Rejected, so the similarities and differences are clear."

        caption_plot.add_layout(Label(x=0, y=380, x_units='screen', y_units='screen', text='{}'.format(caption),
                                      text_font='times', text_font_size='15pt', render_mode='css'))

        # caption_plot.outline_line_color = None
        caption_plot.toolbar_location = None

        # create title plot
        title_plot = figure(width=plot_width, height=50, margin=(0, 0, 0, 0))
        title = '{}: Average Pull Request Event Types for {} Pull Requests'.format(repo_dict[repo_id], description)

        title_plot.add_layout(Label(x=550, y=0, x_units='screen', y_units='screen', text='{}'.format(title),
                                    text_font='times', text_font_size='17px',
                                    text_font_style='bold', render_mode='css'))

        # title_plot.outline_line_color = None
        title_plot.toolbar_location = None

        layout = column([title_plot, grid, caption_plot], sizing_mode='scale_width')

        if return_json == "true":
            var = Response(response=json.dumps(json_item(layout, "average_PR_events_for_closed_PRs")),
                           mimetype='application/json',
                           status=200)

            var.headers["Access-Control-Allow-Orgin"] = "*"

            return var

            # opts = FirefoxOptions()
        # opts.add_argument("--headless")
        # driver = webdriver.Firefox(firefox_options=opts)
        filename = export_png(layout, timeout=181)  # , webdriver=selenium.webdriver.firefox.webdriver)

        return send_file(filename)

    @server.app.route('/{}/pull_request_reports/Average_PR_duration/'.format(server.api_version), methods=["GET"])
    def Average_PR_duration():

        repo_id, start_date, end_date, error = get_repo_id_start_date_and_end_date()

        if error:
            return Response(response=error["message"],
                            mimetype='application/json',
                            status=error["status_code"])
        
        group_by = str(request.args.get('group_by', "month"))
        return_json = request.args.get('return_json', "false")
        remove_outliers = str(request.args.get('remove_outliers', "true"))

        x_axis = 'repo_name'
        group_by = 'merged_flag'
        y_axis = 'closed_yearmonth'
        description = "All Closed"
        heat_field = 'pr_duration_days'
        columns = 2

        df_type = get_df_tuple_locations()

        df_tuple = pull_request_data_collection(repo_id=repo_id, start_date=start_date, end_date=end_date)

        pr_closed = df_tuple[df_type["pr_closed"]]
        needed_columns = ['repo_id', y_axis, group_by, x_axis, 'pr_closed_at', 'pr_created_at']
        pr_closed = filter_data(pr_closed, needed_columns)

        if len(pr_closed) == 0:
            return Response(response="There is no data for this repo, in the database you are accessing",
                            mimetype='application/json',
                            status=200)

        pr_duration_frame = pr_closed.assign(pr_duration=(pr_closed['pr_closed_at'] - pr_closed['pr_created_at']))
        pr_duration_frame = pr_duration_frame.assign(
            pr_duration_days=(pr_duration_frame['pr_duration'] / datetime.timedelta(minutes=1)) / 60 / 24)

        repo_dict = {repo_id: pr_duration_frame.loc[pr_duration_frame['repo_id'] == repo_id].iloc[0]['repo_name']}

        red_green_gradient = linear_gradient('#0080FF', '#DC143C', 150)['hex']  # 32CD32

        driver_df = pr_duration_frame.copy()

        driver_df[y_axis] = driver_df[y_axis].astype(str)

        # add new group by + xaxis column 
        driver_df['grouped_x'] = driver_df[x_axis] + ' - ' + driver_df[group_by]

        driver_df_mean = driver_df.groupby(['grouped_x', y_axis], as_index=False).mean()

        colors = red_green_gradient
        y_groups = driver_df_mean[y_axis].unique()
        x_groups = sorted(driver_df[x_axis].unique())
        grouped_x_groups = sorted(driver_df_mean['grouped_x'].unique())

        # defualt outliers removed to 0
        outliers_removed = 0

        if remove_outliers == "true":
            driver_df_mean, outliers_removed, outlier_cutoff = remove_outliers_by_standard_deviation(driver_df_mean,
                                                                                                     heat_field)

        values = driver_df_mean[heat_field].values.tolist()

        heat_max = max(values) * 1.02

        mapper = LinearColorMapper(palette=colors, low=driver_df_mean[heat_field].min(),
                                   high=heat_max)  # driver_df_mean[heat_field].max())

        source = ColumnDataSource(driver_df_mean)
        title_beginning = repo_dict[repo_id] + ':'
        plot_width = 1100
        p = figure(plot_width=plot_width, plot_height=300,
                   title="{} Mean Duration (Days) {} Pull Requests".format(title_beginning, description),
                   y_range=grouped_x_groups[::-1], x_range=y_groups,
                   toolbar_location=None, tools="")  # , x_axis_location="above")

        for x_group in x_groups:
            outliers = driver_df_mean.loc[
                (driver_df_mean[heat_field] > heat_max) & (driver_df_mean['grouped_x'].str.contains(x_group))]

            if outliers_removed > 0:
                p.add_layout(Title(
                    text="** Outliers capped at {} days: {} outlier(s) for {} were capped at {} **".format(
                        outlier_cutoff, outliers_removed, x_group, outlier_cutoff), align="center"), "below")

        p.rect(x=y_axis, y='grouped_x', width=1, height=1, source=source,
               line_color=None, fill_color=transform(heat_field, mapper))

        color_bar = ColorBar(color_mapper=mapper, location=(0, 0),
                             ticker=BasicTicker(desired_num_ticks=9),
                             formatter=PrintfTickFormatter(format="%d"))

        p.add_layout(color_bar, 'right')

        p.title.align = "center"
        p.title.text_font_size = "16px"

        p.axis.axis_line_color = None
        p.axis.major_tick_line_color = None
        p.axis.major_label_text_font_size = "11pt"
        p.axis.major_label_standoff = 0
        p.xaxis.major_label_orientation = 1.0
        p.xaxis.axis_label = 'Month Closed' if y_axis[0:6] == 'closed' else 'Date Created' if y_axis[
                                                                                              0:7] == 'created' else 'Repository' if y_axis == 'repo_name' else ''
        #     p.yaxis.axis_label = 'Merged Status'

        p.title.text_font_size = "16px"

        p.xaxis.axis_label_text_font_size = "16px"
        p.xaxis.major_label_text_font_size = "14px"

        p.yaxis.major_label_text_font_size = "15px"

        plot = p

        p = figure(width=plot_width, height=200, margin=(0, 0, 0, 0))
        caption = "This graph shows the average duration of all closed pull requests. " \
                  "Red represents a slow response relative to the others, while blue a light blue " \
                  "represents a fast response relative to the others. Blank cells represents months " \
                  "without pull requests."
        p = add_caption_to_plot(p, caption)
        caption_plot = p

        grid = gridplot([[plot], [caption_plot]])

        if return_json == "true":
            var = Response(response=json.dumps(json_item(grid, "Average_PR_duration")),
                           mimetype='application/json',
                           status=200)

            var.headers["Access-Control-Allow-Orgin"] = "*"

            return var

            # opts = FirefoxOptions()
        # opts.add_argument("--headless")
        # driver = webdriver.Firefox(firefox_options=opts)
        # newt = get_screenshot_as_png(grid, timeout=180, webdriver=selenium.webdriver.firefox.webdriver)
        # filename = export_png(grid, timeout=180, webdriver=selenium.webdriver.firefox.webdriver)
        filename = export_png(grid, timeout=180)

        # return sendfile(newt)
        return send_file(filename)
