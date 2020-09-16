import psycopg2
import pandas as pd 
import sqlalchemy as salc
import numpy as np
import warnings
import datetime
import json
from flask import Response, request, send_file
warnings.filterwarnings('ignore')


from bokeh.palettes import Colorblind, mpl, Category20
from bokeh.layouts import gridplot
from bokeh.models.annotations import Title
from bokeh.io import export_png
from bokeh.models import ColumnDataSource, Legend, LabelSet, Range1d, LinearAxis, Label, FactorRange
from bokeh.plotting import figure
from bokeh.models.glyphs import Rect
from bokeh.transform import dodge, factor_cmap

try:
    colors = Colorblind[len(repo_set)]
except:
    colors = Colorblind[3]
#mpl['Plasma'][len(repo_set)]
#['A6CEE3','B2DF8A','33A02C','FB9A99']


def create_routes(server):

    def pull_request_data_collection(repo_id, start_date, end_date, database_connection_string, df_type, slow_20):


        dbschema='augur_data'
        engine = salc.create_engine(
        database_connection_string,
        connect_args={'options': '-csearch_path={}'.format(dbschema)})

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
        pr_all = pd.read_sql(pr_query, con=engine)
    

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
        pr_all[['created_year', 'closed_year']] = pr_all[['created_year', 'closed_year']].fillna(-1).astype(int).astype(str)


        # Get days for average_time_between_responses time delta

        pr_all['average_days_between_responses'] = pr_all['average_time_between_responses'].map(lambda x: x.days).astype(float)
        pr_all['average_hours_between_responses'] = pr_all['average_time_between_responses'].map(lambda x: x.days * 24).astype(float)


        start_date = pd.to_datetime(start_date)
        # end_date = pd.to_datetime('2020-02-01 09:00:00')
        end_date = pd.to_datetime(end_date)
        pr_all = pr_all[(pr_all['pr_created_at'] > start_date) & (pr_all['pr_closed_at'] < end_date)]

        pr_all['created_year'] = pr_all['created_year'].map(int)
        pr_all['created_month'] = pr_all['created_month'].map(int)
        pr_all['created_month'] = pr_all['created_month'].map(lambda x: '{0:0>2}'.format(x))
        pr_all['created_yearmonth'] = pd.to_datetime(pr_all['created_year'].map(str) + '-' + pr_all['created_month'].map(str) + '-01')


        # getting the number of days of (today - created at) for the PRs that are still open
        # and putting this in the days_to_close column

        # get timedeltas of creation time to todays date/time
        days_to_close_open_pr = datetime.datetime.now() - pr_all.loc[pr_all['pr_src_state'] == 'open']['pr_created_at']

        # get num days from above timedelta
        days_to_close_open_pr = days_to_close_open_pr.apply(lambda x: x.days).astype(int)

        # for only OPEN pr's, set the days_to_close column equal to above dataframe
        pr_all.loc[pr_all['pr_src_state'] == 'open'] = pr_all.loc[pr_all['pr_src_state'] == 'open'].assign(days_to_close=days_to_close_open_pr)

        pr_all.loc[pr_all['pr_src_state'] == 'open'].head()


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


        if slow_20 == True:

            if df_type == 'pr_open':
                return pr_slow20_open
            elif df_type == 'pr_closed':
                return pr_slow20_closed
            elif df_type == 'pr_merged':
                return pr_slow20_merged
            elif df_type == 'pr_not_merged':
                return pr_slow20_not_merged
            elif df_type == 'pr_all':
                return pr_slow20_all

        elif(slow_20 == False):

            if df_type == 'pr_open':
                return pr_open
            elif df_type == 'pr_closed':
                return pr_closed
            elif df_type == 'pr_merged':
                return pr_merged
            elif df_type == 'pr_not_merged':
                return pr_not_merged
            elif df_type == 'pr_all':
                return pr_all


    def remove_outliers(input_df, field, num_outliers_repo_map):
        df_no_outliers = input_df.copy()
        for repo_name, num_outliers in num_outliers_repo_map.items():
            indices_to_drop = input_df.loc[input_df['repo_name'] == repo_name].nlargest(num_outliers, field).index
            df_no_outliers = df_no_outliers.drop(index=indices_to_drop)
        return df_no_outliers



    @server.app.route('/{}/pull_request_reports/average_commits_per_PR/'.format(server.api_version), methods=["POST"])
    def average_commits_per_PR():

        repo_id = request.json['repo_id']
        start_date = request.json['start_date']
        end_date = request.json['end_date']

        user = request.json['user']
        password = request.json['password']
        host = request.json['host']
        port = request.json['port']
        database = request.json['database']


        database_connection_string = 'postgres+psycopg2://{}:{}@{}:{}/{}'.format(user, password, host, port, database)

        input_df = pull_request_data_collection(repo_id=repo_id, start_date=start_date, end_date=end_date, database_connection_string=database_connection_string, slow_20=False, df_type='pr_all')

        x_axis = 'closed_year'
        y_axis = 'num_commits'
        group_by = 'merged_flag'
        description = 'All'  


        repo_dict = {repo_id : input_df.loc[input_df['repo_id'] == repo_id].iloc[0]['repo_name']}   
       

        driver_df = input_df.copy() # deep copy input data so we do not change the external dataframe 

        # Change closed year to int so that doesn't display as 2019.0 for example
        driver_df['closed_year'] = driver_df['closed_year'].astype(int).astype(str)

        # contains the closed years
        x_groups = sorted(list(driver_df[x_axis].unique()))

        # inner groups on x_axis they are merged and not_merged
        groups = list(driver_df[group_by].unique())

        # setup color pallete
        try:
            colors = mpl['Plasma'][len(groups)]
        except:
            colors = [mpl['Plasma'][3][0]] + [mpl['Plasma'][3][1]]

        merged_avg_values = list(driver_df.loc[driver_df[group_by] == 'Merged / Accepted'].groupby([x_axis],as_index=False).mean().round(1)['commit_count'])
        not_merged_avg_values = list(driver_df.loc[driver_df[group_by] == 'Not Merged / Rejected'].groupby([x_axis],as_index=False).mean().round(1)['commit_count'])


        # Setup data in format for grouped bar chart
        data = {
                'years'                   : x_groups,
                'Merged / Accepted'       : merged_avg_values,
                'Not Merged / Rejected'   : not_merged_avg_values,
            }

        x = [ (year, pr_state) for year in x_groups for pr_state in groups ]
        counts = sum(zip(data['Merged / Accepted'], data['Not Merged / Rejected']), ())

        source = ColumnDataSource(data=dict(x=x, counts=counts))

        title_beginning = '{}: '.format(repo_dict[repo_id])
        title="{}Average Commit Counts Per Year for {} Pull Requests".format(title_beginning, description)
        
        plot_width = len(x_groups) * 300
        title_text_font_size = 16 
        
        if (len(title) * title_text_font_size / 2) > plot_width:
            plot_width = int(len(title) * title_text_font_size / 2) + 40
        
        p = figure(x_range=FactorRange(*x), plot_height=450, plot_width=plot_width, title=title, y_range=(0, max(merged_avg_values + not_merged_avg_values)*1.15), toolbar_location=None)

        # Vertical bar glyph
        p.vbar(x='x', top='counts', width=0.9, source=source, line_color="white",
               fill_color=factor_cmap('x', palette=colors, factors=groups, start=1, end=2))

        # Data label 
        labels = LabelSet(x='x', y='counts', text='counts',# y_offset=-8, x_offset=34,
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

        p = figure(width = plot_width, height=200, margin = (0, 0, 0, 0))
        caption = "This graph shows the average commits per pull requests over an entire year, for merged and not merged pull requests."
        p.add_layout(Label(
        x = 0, # Change to shift caption left or right
        y = 160, 
        x_units = 'screen',
        y_units = 'screen',
        text='{}'.format(caption),
        text_font = 'times', # Use same font as paper
        text_font_size = '15pt',
        render_mode='css'
        ))
        p.outline_line_color = None

        caption_plot = p

        grid = gridplot([[plot], [caption_plot]])

        filename = export_png(grid)
        
        return send_file(filename)



    @server.app.route('/{}/pull_request_reports/average_comments_per_PR/'.format(server.api_version), methods=["POST"])
    def average_comments_per_PR():

        repo_id = request.json['repo_id']
        start_date = request.json['start_date']
        end_date = request.json['end_date']

        user = request.json['user']
        password = request.json['password']
        host = request.json['host']
        port = request.json['port']
        database = request.json['database']


        database_connection_string = 'postgres+psycopg2://{}:{}@{}:{}/{}'.format(user, password, host, port, database)

        input_df = pull_request_data_collection(repo_id=repo_id, start_date=start_date, end_date=end_date, database_connection_string=database_connection_string, slow_20=False, df_type='pr_closed')

        group_by = 'merged_flag'
        x_axis = 'comment_count'
        description = "All Closed"
        y_axis = 'closed_year'  

        repo_dict = {repo_id : input_df.loc[input_df['repo_id'] == repo_id].iloc[0]['repo_name']}   
  

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
        p = figure(y_range=y_groups, plot_height=450, plot_width=plot_width, # y_range=y_groups,#(pr_all[y_axis].min(),pr_all[y_axis].max()) #y_axis_type="datetime",
                   title='{} {}'.format(title_beginning, "Mean Comments for {} Pull Requests".format(description)), toolbar_location=None)

        possible_maximums= []
        for y_value in y_groups:

            y_merged_data = driver_df.loc[(driver_df[y_axis] == y_value) & (driver_df['merged_flag'] == 'Merged / Accepted')]
            y_not_merged_data = driver_df.loc[(driver_df[y_axis] == y_value) & (driver_df['merged_flag'] == 'Not Merged / Rejected')]

            if len(y_merged_data) > 0:
                y_merged_data[x_axis + '_mean'] = y_merged_data[x_axis].mean().round(1)
            else:
                y_merged_data[x_axis + '_mean'] = 0.00

            if len(y_not_merged_data) > 0:
                y_not_merged_data[x_axis + '_mean'] = y_not_merged_data[x_axis].mean().round(1)
            else:
                y_not_merged_data[x_axis + '_mean'] = 0

            not_merged_source = ColumnDataSource(y_not_merged_data)
            merged_source = ColumnDataSource(y_merged_data)

            possible_maximums.append(max(y_not_merged_data[x_axis + '_mean']))
            possible_maximums.append(max(y_merged_data[x_axis + '_mean']))

            # mean comment count for merged
            merged_comment_count_glyph = p.hbar(y=dodge(y_axis, -0.1, range=p.y_range), left=0, right=x_axis + '_mean', height=0.04*len(driver_df[y_axis].unique()), 
                                         source=merged_source, fill_color="black")#,legend_label="Mean Days to Close",
            # Data label 
            labels = LabelSet(x=x_axis + '_mean', y=dodge(y_axis, -0.1, range=p.y_range), text=x_axis + '_mean', y_offset=-8, x_offset=34,
                      text_font_size="12pt", text_color="black",
                      source=merged_source, text_align='center')
            p.add_layout(labels)
            # mean comment count For nonmerged
            not_merged_comment_count_glyph = p.hbar(y=dodge(y_axis, 0.1, range=p.y_range), left=0, right=x_axis + '_mean', 
                                         height=0.04*len(driver_df[y_axis].unique()), source=not_merged_source, fill_color="#e84d60")#legend_label="Mean Days to Close",
            # Data label 
            labels = LabelSet(x=x_axis + '_mean', y=dodge(y_axis, 0.1, range=p.y_range), text=x_axis + '_mean', y_offset=-8, x_offset=34,
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

        p.x_range = Range1d(0, max(possible_maximums)*1.15)
        
        plot = p
        
        p = figure(width = plot_width, height=200, margin = (0, 0, 0, 0))
        caption = "This graph shows the average number of comments per merged or not merged pull request."
        p.add_layout(Label(
        x = 0, # Change to shift caption left or right
        y = 160, 
        x_units = 'screen',
        y_units = 'screen',
        text='{}'.format(caption),
        text_font = 'times', # Use same font as paper
        text_font_size = '15pt',
        render_mode='css'
        ))
        p.outline_line_color = None

        caption_plot = p

        grid = gridplot([[plot], [caption_plot]])

       
        filename = export_png(grid)
        
        return send_file(filename)

    @server.app.route('/{}/pull_request_reports/PR_counts_by_merged_status/'.format(server.api_version), methods=["POST"])
    def PR_counts_by_merged_status():

        repo_id = request.json['repo_id']
        start_date = request.json['start_date']
        end_date = request.json['end_date']

        user = request.json['user']
        password = request.json['password']
        host = request.json['host']
        port = request.json['port']
        database = request.json['database']


        database_connection_string = 'postgres+psycopg2://{}:{}@{}:{}/{}'.format(user, password, host, port, database)

        pr_closed = pull_request_data_collection(repo_id=repo_id, start_date=start_date, end_date=end_date, database_connection_string=database_connection_string, slow_20=False, df_type='pr_closed')
        pr_slow20_not_merged = pull_request_data_collection(repo_id=repo_id, start_date=start_date, end_date=end_date, database_connection_string=database_connection_string, slow_20=True, df_type='pr_not_merged')
        pr_slow20_merged = pull_request_data_collection(repo_id=repo_id, start_date=start_date, end_date=end_date, database_connection_string=database_connection_string, slow_20=True, df_type='pr_merged')

        x_axis='closed_year'
        description='All Closed'
       

        repo_dict = {repo_id : pr_closed.loc[pr_closed['repo_id'] == repo_id].iloc[0]['repo_name']}   
  
        data_dict = {'All':pr_closed,'Slowest 20%':pr_slow20_not_merged.append(pr_slow20_merged,ignore_index=True)}

        colors = mpl['Plasma'][6]

        #if repo_name == 'mbed-os':
            #colors = colors[::-1]

        for data_desc, input_df in data_dict.items():
            x_groups = sorted(list(input_df[x_axis].astype(str).unique()))
            break

        plot_width = 315 * len(x_groups)
        title_beginning = repo_dict[repo_id] 
        p = figure(x_range=x_groups, plot_height=350, plot_width=plot_width,  
                   title='{}: {}'.format(title_beginning, "Count of {} Pull Requests by Merged Status".format(description)), toolbar_location=None)

        dodge_amount = 0.12
        color_index = 0
        x_offset = 50

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

                len_merged_entry = len(driver_df.loc[(driver_df['merged_flag'] == 'Merged / Accepted') & (driver_df[x_axis] == x_group)])
                totals += [len(driver_df.loc[(driver_df['merged_flag'] == 'Not Merged / Rejected') & (driver_df[x_axis] == x_group)]) + len_merged_entry]
                len_not_merged += [len(driver_df.loc[(driver_df['merged_flag'] == 'Not Merged / Rejected') & (driver_df[x_axis] == x_group)])]
                len_merged += [len_merged_entry]
                zeros.append(0)

            data = {'X': x_groups}
            for group in groups:
                data[group] = []
                for x_group in x_groups:
                    data[group] += [len(driver_df.loc[(driver_df['merged_flag'] == group) & (driver_df[x_axis] == x_group)])]

            data['len_merged'] = len_merged
            data['len_not_merged'] = len_not_merged
            data['totals'] = totals
            data['zeros'] = zeros

            if data_desc == "All":
                all_totals = totals

            source = ColumnDataSource(data)

            stacked_bar = p.vbar_stack(groups, x=dodge('X', dodge_amount, range=p.x_range), width=0.2, source=source, color=colors[1:3], legend_label=[f"{data_desc} " + "%s" % x for x in groups])
            # Data label for merged

            p.add_layout(
                LabelSet(x=dodge('X', dodge_amount, range=p.x_range), y='zeros', text='len_merged', y_offset=2, x_offset=x_offset,
                      text_font_size="12pt", text_color=colors[1:3][0],
                      source=source, text_align='center')
            )
            if min(data['totals']) < 400:
                y_offset = 15
            else:
                y_offset = 0
            # Data label for not merged
            p.add_layout(
                LabelSet(x=dodge('X', dodge_amount, range=p.x_range), y='totals', text='len_not_merged', y_offset=y_offset, x_offset=x_offset,
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

        p.y_range = Range1d(0,  max(all_totals)*1.4)

        p.xgrid.grid_line_color = None
        p.legend.location = "top_center"
        p.legend.orientation="horizontal"
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
        
        p = figure(width = plot_width, height=200, margin = (0, 0, 0, 0))
        caption = "This graph shows the number of closed pull requests per year in four different categories. These four categories are All Merged, All Not Merged, Slowest 20% Merged, and Slowest 20% Not Merged."
        p.add_layout(Label(
        x = 0, # Change to shift caption left or right
        y = 160, 
        x_units = 'screen',
        y_units = 'screen',
        text='{}'.format(caption),
        text_font = 'times', # Use same font as paper
        text_font_size = '15pt',
        render_mode='css'
        ))
        p.outline_line_color = None

        caption_plot = p

        grid = gridplot([[plot], [caption_plot]])
        
        filename = export_png(grid)
        
        return send_file(filename)










    @server.app.route('/{}/pull_request_reports/mean_response_times_for_PR/'.format(server.api_version), methods=["POST"])
    def mean_response_times_for_PR():

        repo_id = request.json['repo_id']
        start_date = request.json['start_date']
        end_date = request.json['end_date']

        user = request.json['user']
        password = request.json['password']
        host = request.json['host']
        port = request.json['port']
        database = request.json['database']


        database_connection_string = 'postgres+psycopg2://{}:{}@{}:{}/{}'.format(user, password, host, port, database)

        input_df = pull_request_data_collection(repo_id=repo_id, start_date=start_date, end_date=end_date, database_connection_string=database_connection_string, slow_20=False, df_type='pr_closed')   

        time_unit='days'
        x_max = 95
        y_axis = 'closed_year'
        description = "All Closed"
        legend_position=(410, 10)

        repo_dict = {repo_id : input_df.loc[input_df['repo_id'] == repo_id].iloc[0]['repo_name']}   

        driver_df = input_df.copy()[['repo_name', 'repo_id', 'merged_flag', y_axis, time_unit + '_to_first_response', time_unit + '_to_last_response', 
                                     time_unit + '_to_close']] # deep copy input data so we do not alter the external dataframe


        title_beginning = '{}: '.format(repo_dict[repo_id])
        plot_width = 950
        p = figure(toolbar_location=None, y_range=sorted(driver_df[y_axis].unique()), plot_width=plot_width, 
                   plot_height=450,#75*len(driver_df[y_axis].unique()),
                   title="{}Mean Response Times for Pull Requests {}".format(title_beginning, description))

        first_response_glyphs = []
        last_response_glyphs = []
        merged_days_to_close_glyphs = []
        not_merged_days_to_close_glyphs = []

        possible_maximums = []
        
        
        for y_value in driver_df[y_axis].unique():

            y_merged_data = driver_df.loc[(driver_df[y_axis] == y_value) & (driver_df['merged_flag'] == 'Merged / Accepted')]
            y_not_merged_data = driver_df.loc[(driver_df[y_axis] == y_value) & (driver_df['merged_flag'] == 'Not Merged / Rejected')]

            y_merged_data[time_unit + '_to_first_response_mean'] = y_merged_data[time_unit + '_to_first_response'].mean().round(1) if len(y_merged_data) > 0 else 0.00
            y_merged_data[time_unit + '_to_last_response_mean'] = y_merged_data[time_unit + '_to_last_response'].mean().round(1) if len(y_merged_data) > 0 else 0.00
            y_merged_data[time_unit + '_to_close_mean'] = y_merged_data[time_unit + '_to_close'].mean().round(1) if len(y_merged_data) > 0 else 0.00

            y_not_merged_data[time_unit + '_to_first_response_mean'] = y_not_merged_data[time_unit + '_to_first_response'].mean().round(1) if len(y_not_merged_data) > 0 else 0.00
            y_not_merged_data[time_unit + '_to_last_response_mean'] = y_not_merged_data[time_unit + '_to_last_response'].mean().round(1) if len(y_not_merged_data) > 0 else 0.00
            y_not_merged_data[time_unit + '_to_close_mean'] = y_not_merged_data[time_unit + '_to_close'].mean().round(1) if len(y_not_merged_data) > 0 else 0.00

            possible_maximums.append(max(y_merged_data[time_unit + '_to_close_mean']))
            possible_maximums.append(max(y_not_merged_data[time_unit + '_to_close_mean']))
            
            maximum = max(possible_maximums)*1.15
            ideal_difference = maximum*0.064
            
        for y_value in driver_df[y_axis].unique():

            y_merged_data = driver_df.loc[(driver_df[y_axis] == y_value) & (driver_df['merged_flag'] == 'Merged / Accepted')]
            y_not_merged_data = driver_df.loc[(driver_df[y_axis] == y_value) & (driver_df['merged_flag'] == 'Not Merged / Rejected')]

            y_merged_data[time_unit + '_to_first_response_mean'] = y_merged_data[time_unit + '_to_first_response'].mean().round(1) if len(y_merged_data) > 0 else 0.00
            y_merged_data[time_unit + '_to_last_response_mean'] = y_merged_data[time_unit + '_to_last_response'].mean().round(1) if len(y_merged_data) > 0 else 0.00
            y_merged_data[time_unit + '_to_close_mean'] = y_merged_data[time_unit + '_to_close'].mean().round(1) if len(y_merged_data) > 0 else 0.00

            y_not_merged_data[time_unit + '_to_first_response_mean'] = y_not_merged_data[time_unit + '_to_first_response'].mean().round(1) if len(y_not_merged_data) > 0 else 0.00
            y_not_merged_data[time_unit + '_to_last_response_mean'] = y_not_merged_data[time_unit + '_to_last_response'].mean().round(1) if len(y_not_merged_data) > 0 else 0.00
            y_not_merged_data[time_unit + '_to_close_mean'] = y_not_merged_data[time_unit + '_to_close'].mean().round(1) if len(y_not_merged_data) > 0 else 0.00

            not_merged_source = ColumnDataSource(y_not_merged_data)
            merged_source = ColumnDataSource(y_merged_data)

            # mean PR length for merged
            merged_days_to_close_glyph = p.hbar(y=dodge(y_axis, -0.1, range=p.y_range), left=0, right=time_unit + '_to_close_mean', height=0.04*len(driver_df[y_axis].unique()), 
                                         source=merged_source, fill_color="black")#,legend_label="Mean Days to Close",
            merged_days_to_close_glyphs.append(merged_days_to_close_glyph)
            # Data label 
            labels = LabelSet(x=time_unit + '_to_close_mean', y=dodge(y_axis, -0.1, range=p.y_range), text=time_unit + '_to_close_mean', y_offset=-8, x_offset=34, #34
                      text_font_size="12pt", text_color="black",
                      source=merged_source, text_align='center')
            p.add_layout(labels)


            # mean PR length For nonmerged
            not_merged_days_to_close_glyph = p.hbar(y=dodge(y_axis, 0.1, range=p.y_range), left=0, right=time_unit + '_to_close_mean', 
                                         height=0.04*len(driver_df[y_axis].unique()), source=not_merged_source, fill_color="#e84d60")#legend_label="Mean Days to Close",
            not_merged_days_to_close_glyphs.append(not_merged_days_to_close_glyph)
            # Data label 
            labels = LabelSet(x=time_unit + '_to_close_mean', y=dodge(y_axis, 0.1, range=p.y_range), text=time_unit + '_to_close_mean', y_offset=-8, x_offset=44,
                      text_font_size="12pt", text_color="#e84d60",
                      source=not_merged_source, text_align='center')
            p.add_layout(labels)

            
            #if the difference between two values is less than 6.4 percent move the second one to the right 30 pixels
            if (max(y_merged_data[time_unit + '_to_last_response_mean']) - max(y_merged_data[time_unit + '_to_first_response_mean'])) < ideal_difference:
                merged_x_offset = 30
            else:
                merged_x_offset = 0
                
            #if the difference between two values is less than 6.4 percent move the second one to the right 30 pixels
            if (max(y_not_merged_data[time_unit + '_to_last_response_mean']) - max(y_not_merged_data[time_unit + '_to_first_response_mean'])) < ideal_difference:
                not_merged_x_offset = 30
            else:
                not_merged_x_offset = 0
                
            #if there is only one bar set the y_offsets so the labels will not overlap the bars
            if len(driver_df[y_axis].unique()) == 1:
                merged_y_offset = -65
                not_merged_y_offset = 45
            else:
                merged_y_offset = -45
                not_merged_y_offset = 25
            
            
            # mean time to first response
            glyph = Rect(x=time_unit + '_to_first_response_mean', y=dodge(y_axis, -0.1, range=p.y_range), width=x_max/100, height=0.08*len(driver_df[y_axis].unique()), fill_color=colors[0])
            first_response_glyph = p.add_glyph(merged_source, glyph)
            first_response_glyphs.append(first_response_glyph)
            # Data label 
            labels = LabelSet(x=time_unit + '_to_first_response_mean', y=dodge(y_axis, 0, range=p.y_range),text=time_unit + '_to_first_response_mean',x_offset = 0, y_offset=merged_y_offset,#-60,
                      text_font_size="12pt", text_color=colors[0],
                      source=merged_source, text_align='center')
            p.add_layout(labels)

            #for nonmerged
            glyph = Rect(x=time_unit + '_to_first_response_mean', y=dodge(y_axis, 0.1, range=p.y_range), width=x_max/100, height=0.08*len(driver_df[y_axis].unique()), fill_color=colors[0])
            first_response_glyph = p.add_glyph(not_merged_source, glyph)
            first_response_glyphs.append(first_response_glyph)
            # Data label 
            labels = LabelSet(x=time_unit + '_to_first_response_mean', y=dodge(y_axis, 0, range=p.y_range),text=time_unit + '_to_first_response_mean',x_offset = 0, y_offset=not_merged_y_offset,#40,
                              text_font_size="12pt", text_color=colors[0],
                      source=not_merged_source, text_align='center')
            p.add_layout(labels)


            # mean time to last response
            glyph = Rect(x=time_unit + '_to_last_response_mean', y=dodge(y_axis, -0.1, range=p.y_range), width=x_max/100, height=0.08*len(driver_df[y_axis].unique()), fill_color=colors[1])
            last_response_glyph = p.add_glyph(merged_source, glyph)
            last_response_glyphs.append(last_response_glyph)
            # Data label 
            labels = LabelSet(x=time_unit + '_to_last_response_mean', y=dodge(y_axis, 0, range=p.y_range), text=time_unit + '_to_last_response_mean', x_offset=merged_x_offset, y_offset=merged_y_offset,#-60,
                      text_font_size="12pt", text_color=colors[1],
                      source=merged_source, text_align='center')
            p.add_layout(labels)
            

            #for nonmerged
            glyph = Rect(x=time_unit + '_to_last_response_mean', y=dodge(y_axis, 0.1, range=p.y_range), width=x_max/100, height=0.08*len(driver_df[y_axis].unique()), fill_color=colors[1])
            last_response_glyph = p.add_glyph(not_merged_source, glyph)
            last_response_glyphs.append(last_response_glyph)
            # Data label 
            labels = LabelSet(x=time_unit + '_to_last_response_mean', y=dodge(y_axis, 0, range=p.y_range), text=time_unit + '_to_last_response_mean', x_offset = not_merged_x_offset, y_offset=not_merged_y_offset,#40,
                      text_font_size="12pt", text_color=colors[1],
                      source=not_merged_source, text_align='center')
            p.add_layout(labels)

        p.title.align = "center"
        p.title.text_font_size = "16px"

        p.xaxis.axis_label = "Days to Close"
        p.xaxis.axis_label_text_font_size = "16px"
        p.xaxis.major_label_text_font_size = "16px"
        
        #adjust the starting point and ending point based on the maximum of maximum of the graph
        p.x_range = Range1d(maximum/30 * -1, maximum*1.15)

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
        add_legend(legend_position, "vertical", "right")
        
        plot = p
        
        p = figure(width = plot_width, height = 200, margin = (0, 0, 0, 0))
        caption = "Caption Here"
        p.add_layout(Label(
        x = 0, # Change to shift caption left or right
        y = 160, 
        x_units = 'screen',
        y_units = 'screen',
        text='{}'.format(caption),
        text_font = 'times', # Use same font as paper
        text_font_size = '15pt',
        render_mode='css'
        ))
        p.outline_line_color = None

        caption_plot = p

        grid = gridplot([[plot], [caption_plot]])


        
        filename = export_png(grid)
        
        return send_file(filename)

