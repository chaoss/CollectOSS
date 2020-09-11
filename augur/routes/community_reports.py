import base64
import pandas as pd
import json
from flask import Response, request, send_file

#import visualization libraries
from bokeh.io import output_notebook, show, output_file
from bokeh.io.export import get_screenshot_as_png
from bokeh.plotting import figure
from bokeh.models import Label, LabelSet, ColumnDataSource, Legend
from bokeh.palettes import Colorblind
from bokeh.layouts import gridplot
from bokeh.transform import cumsum

import psycopg2


import sqlalchemy as salc
import numpy as np
import warnings
import datetime
warnings.filterwarnings('ignore')

from selenium import webdriver


from math import pi

#from augur.routes.new_contributor_query import *

def create_routes(server):

    @server.app.route('/{}/reports/new_contributors/'.format(server.api_version), methods=["POST"])
    def new_contributors_report():
        #type = request.headers.get_header('application/json')

        repo_id = request.json['repo_id']
        start_date = request.json['start_date']
        end_date = request.json['end_date']
        group_by = request.json['group_by']
        required_contributions = request.json['required_contributions']
        required_time = request.json['required_time']

        user = request.json['user']
        password = request.json['password']
        host = request.json['host']
        port = request.json['port']
        database = request.json['database']



        #def vertical_bar_chart(repo_id, start_date, end_date, group_by, y_axis='new_contributors', title = "{}: {} {} Time Contributors Per {}", required_contributions = 4, required_time = 5):



        jupyter_execution = False

        database_connection_string = 'postgres+psycopg2://{}:{}@{}:{}/{}'.format(user, password, host, port, database)

        dbschema='augur_data'
        engine = salc.create_engine(
            database_connection_string,
            connect_args={'options': '-csearch_path={}'.format(dbschema)})

        rank_list = []
        for num in range(1, required_contributions + 1):
            rank_list.append(num)
        rank_tuple = tuple(rank_list)


        df = pd.DataFrame()


        pr_query = salc.sql.text(f"""        
        

            SELECT * FROM (
                SELECT ID AS
                    cntrb_id,
                    A.created_at AS created_at,
                    date_part('month', A.created_at::DATE) AS month,
                    date_part('year', A.created_at::DATE) AS year,
                    A.repo_id,
                    repo_name,
                    full_name,
                    login,
                ACTION,
                rank() OVER (
                        PARTITION BY id
                        ORDER BY A.created_at ASC
                    )
                FROM
                    (
                        (
                        SELECT
                            canonical_id AS ID,
                            created_at AS created_at,
                            repo_id,
                            'issue_opened' AS ACTION,
                            contributors.cntrb_full_name AS full_name,
                            contributors.cntrb_login AS login 
                        FROM
                            augur_data.issues
                            LEFT OUTER JOIN augur_data.contributors ON contributors.cntrb_id = issues.reporter_id
                            LEFT OUTER JOIN ( SELECT DISTINCT ON ( cntrb_canonical ) cntrb_full_name, cntrb_canonical AS canonical_email, data_collection_date, cntrb_id AS canonical_id 
                            FROM augur_data.contributors WHERE cntrb_canonical = cntrb_email ORDER BY cntrb_canonical 
                            ) canonical_full_names ON canonical_full_names.canonical_email = contributors.cntrb_canonical 
                        WHERE
                            repo_id = {repo_id}
                            AND pull_request IS NULL 
                        GROUP BY
                            canonical_id,
                            repo_id,
                            issues.created_at,
                            contributors.cntrb_full_name,
                            contributors.cntrb_login 
                        ) UNION ALL
                        (
                        SELECT
                            canonical_id AS ID,
                            TO_TIMESTAMP( cmt_author_date, 'YYYY-MM-DD' ) AS created_at,
                            repo_id,
                            'commit' AS ACTION,
                            contributors.cntrb_full_name AS full_name,
                            contributors.cntrb_login AS login 
                        FROM
                            augur_data.commits
                            LEFT OUTER JOIN augur_data.contributors ON cntrb_email = cmt_author_email
                            LEFT OUTER JOIN ( SELECT DISTINCT ON ( cntrb_canonical ) cntrb_full_name, cntrb_canonical AS canonical_email, data_collection_date, cntrb_id AS canonical_id 
                            FROM augur_data.contributors WHERE cntrb_canonical = cntrb_email ORDER BY cntrb_canonical 
                            ) canonical_full_names ON canonical_full_names.canonical_email = contributors.cntrb_canonical 
                        WHERE
                            repo_id = {repo_id} 
                        GROUP BY
                            repo_id,
                            canonical_email,
                            canonical_id,
                            commits.cmt_author_date,
                            contributors.cntrb_full_name,
                            contributors.cntrb_login 
                        ) UNION ALL
                        (
                        SELECT
                            message.cntrb_id AS ID,
                            created_at AS created_at,
                            commits.repo_id,
                            'commit_comment' AS ACTION,
                            contributors.cntrb_full_name AS full_name,
                            contributors.cntrb_login AS login
              
                        FROM
                            augur_data.commit_comment_ref,
                            augur_data.commits,
                            augur_data.message
                            LEFT OUTER JOIN augur_data.contributors ON contributors.cntrb_id = message.cntrb_id
                            LEFT OUTER JOIN ( SELECT DISTINCT ON ( cntrb_canonical ) cntrb_full_name, cntrb_canonical AS canonical_email, data_collection_date, cntrb_id AS canonical_id 
                            FROM augur_data.contributors WHERE cntrb_canonical = cntrb_email ORDER BY cntrb_canonical 
                            ) canonical_full_names ON canonical_full_names.canonical_email = contributors.cntrb_canonical 
                        WHERE
                            commits.cmt_id = commit_comment_ref.cmt_id 
                            AND commits.repo_id = {repo_id} 
                            AND commit_comment_ref.msg_id = message.msg_id
         
                        GROUP BY
                            ID,
                            commits.repo_id,
                            commit_comment_ref.created_at,
                            contributors.cntrb_full_name,
                            contributors.cntrb_login
                        ) UNION ALL
                        (
                        SELECT
                            issue_events.cntrb_id AS ID,
                            issue_events.created_at AS created_at,
                            repo_id,
                            'issue_closed' AS ACTION,
                            contributors.cntrb_full_name AS full_name,
                            contributors.cntrb_login AS login 
                        FROM
                            augur_data.issues,
                            augur_data.issue_events
                            LEFT OUTER JOIN augur_data.contributors ON contributors.cntrb_id = issue_events.cntrb_id
                            LEFT OUTER JOIN ( SELECT DISTINCT ON ( cntrb_canonical ) cntrb_full_name, cntrb_canonical AS canonical_email, data_collection_date, cntrb_id AS canonical_id 
                            FROM augur_data.contributors WHERE cntrb_canonical = cntrb_email ORDER BY cntrb_canonical 
                            ) canonical_full_names ON canonical_full_names.canonical_email = contributors.cntrb_canonical 
                        WHERE
                            issues.repo_id = {repo_id} 
                            AND issues.issue_id = issue_events.issue_id 
                            AND issues.pull_request IS NULL 
                            AND issue_events.cntrb_id IS NOT NULL 
                            AND ACTION = 'closed' 
                        GROUP BY
                            issue_events.cntrb_id,
                            repo_id,
                            issue_events.created_at,
                            contributors.cntrb_full_name,
                            contributors.cntrb_login 
                        ) UNION ALL
                        (
                        SELECT
                            pr_augur_contributor_id AS ID,
                            pr_created_at AS created_at,
                            repo_id,
                            'open_pull_request' AS ACTION,
                            contributors.cntrb_full_name AS full_name,
                            contributors.cntrb_login AS login 
                        FROM
                            augur_data.pull_requests
                            LEFT OUTER JOIN augur_data.contributors ON pull_requests.pr_augur_contributor_id = contributors.cntrb_id
                            LEFT OUTER JOIN ( SELECT DISTINCT ON ( cntrb_canonical ) cntrb_full_name, cntrb_canonical AS canonical_email, data_collection_date, cntrb_id AS canonical_id 
                            FROM augur_data.contributors WHERE cntrb_canonical = cntrb_email ORDER BY cntrb_canonical 
                            ) canonical_full_names ON canonical_full_names.canonical_email = contributors.cntrb_canonical 
                        WHERE
                            pull_requests.repo_id = {repo_id} 
                        GROUP BY
                            pull_requests.pr_augur_contributor_id,
                            pull_requests.repo_id,
                            pull_requests.pr_created_at,
                            contributors.cntrb_full_name,
                            contributors.cntrb_login 
                        ) UNION ALL
                        (
                        SELECT
                            message.cntrb_id AS ID,
                            msg_timestamp AS created_at,
                            repo_id,
                            'pull_request_comment' AS ACTION,
                            contributors.cntrb_full_name AS full_name,
                            contributors.cntrb_login AS login 
                        FROM
                            augur_data.pull_requests,
                            augur_data.pull_request_message_ref,
                            augur_data.message
                            LEFT OUTER JOIN augur_data.contributors ON contributors.cntrb_id = message.cntrb_id
                            LEFT OUTER JOIN ( SELECT DISTINCT ON ( cntrb_canonical ) cntrb_full_name, cntrb_canonical AS canonical_email, data_collection_date, cntrb_id AS canonical_id 
                            FROM augur_data.contributors WHERE cntrb_canonical = cntrb_email ORDER BY cntrb_canonical 
                            ) canonical_full_names ON canonical_full_names.canonical_email = contributors.cntrb_canonical 
                        WHERE
                            pull_requests.repo_id = {repo_id}
                            AND pull_request_message_ref.pull_request_id = pull_requests.pull_request_id 
                            AND pull_request_message_ref.msg_id = message.msg_id 
                        GROUP BY
                            message.cntrb_id,
                            pull_requests.repo_id,
                            message.msg_timestamp,
                            contributors.cntrb_full_name,
                            contributors.cntrb_login 
                        ) UNION ALL
                        (
                        SELECT
                            issues.reporter_id AS ID,
                            msg_timestamp AS created_at,
                            repo_id,
                            'issue_comment' AS ACTION,
                            contributors.cntrb_full_name AS full_name,
                            contributors.cntrb_login AS login 
                        FROM
                            issues,
                            issue_message_ref,
                            message
                            LEFT OUTER JOIN augur_data.contributors ON contributors.cntrb_id = message.cntrb_id
                            LEFT OUTER JOIN ( SELECT DISTINCT ON ( cntrb_canonical ) cntrb_full_name, cntrb_canonical AS canonical_email, data_collection_date, cntrb_id AS canonical_id 
                            FROM augur_data.contributors WHERE cntrb_canonical = cntrb_email ORDER BY cntrb_canonical 
                            ) canonical_full_names ON canonical_full_names.canonical_email = contributors.cntrb_canonical 
                        WHERE
                            issues.repo_id = {repo_id}
                            AND issue_message_ref.msg_id = message.msg_id 
                            AND issues.issue_id = issue_message_ref.issue_id
                            AND issues.pull_request_id = NULL
                        GROUP BY
                            issues.reporter_id,
                            issues.repo_id,
                            message.msg_timestamp,
                            contributors.cntrb_full_name,
                            contributors.cntrb_login 
                        ) 
                    ) A,
                    repo 
                WHERE
                ID IS NOT NULL 
                    AND A.repo_id = repo.repo_id 
                GROUP BY
                    A.ID,
                    A.repo_id,
                    A.ACTION,
                    A.created_at,
                    repo.repo_name,
                    A.full_name,
                    A.login
                ORDER BY 
                    cntrb_id
                ) b
                WHERE RANK IN {rank_tuple}

    """)
        df_first_repo = pd.read_sql(pr_query, con=engine)
        if not df.empty: 
            df = pd.concat([df, df_first_repo]) 
        else: 
            # first repo
            df = df_first_repo



        df = df.loc[~df['full_name'].str.contains('bot', na=False)]
        df = df.loc[~df['login'].str.contains('bot', na=False)]

        df = df.loc[~df['cntrb_id'].isin(df[df.duplicated(['cntrb_id', 'created_at', 'repo_id', 'rank'])]['cntrb_id'])]




        #add yearmonths to contributor
        df[['month', 'year']] = df[['month', 'year']].astype(int).astype(str)
        df['yearmonth'] = df['month'] + '/' + df['year']
        df['yearmonth'] = pd.to_datetime(df['yearmonth'])

        # add column with every value being one, so when the contributor df is concatenated with the months df, the filler months won't be counted in the sums
        df['new_contributors'] = 1

        def quarters(month, year):
            if month >= 1 and month <=3:
                return '01' + '/' + year
            elif month >=4 and month <=6:
                return '04' + '/' + year
            elif month >= 5 and month <=9:
                return '07' + '/' + year
            elif month >= 10 and month <= 12:
                return '10' + '/' + year

        #add quarters to contributor dataframe
        df['month'] = df['month'].astype(int)
        df['quarter'] = df.apply(lambda x: quarters(x['month'], x['year']), axis=1)
        df['quarter'] = pd.to_datetime(df['quarter'])



        months_df = pd.DataFrame()


        #with open("report_config.json") as config_file:
        #    config = json.load(config_file)

        jupyter_execution = False


     

        dbschema='augur_data'
        engine = salc.create_engine(
            database_connection_string,
            connect_args={'options': '-csearch_path={}'.format(dbschema)})

        #months_query makes a df of years and months, this is used to fill the months with no data in the visualizaitons
        months_query = salc.sql.text(f"""        
              SELECT
                        *
                    FROM
                    (
                    SELECT
                        date_part( 'year', created_month :: DATE ) AS year,
                        date_part( 'month', created_month :: DATE ) AS MONTH
                    FROM
                        (SELECT * FROM ( SELECT created_month :: DATE FROM generate_series (TIMESTAMP '{start_date}', TIMESTAMP '{end_date}', INTERVAL '1 month' ) created_month ) d ) x 
                    ) y
        """)
        months_df = pd.read_sql(months_query, con=engine)



        #add yearmonths to months_df
        months_df[['year','month']] = months_df[['year','month']].astype(float).astype(int).astype(str)
        months_df['yearmonth'] = months_df['month'] + '/' + months_df['year']
        months_df['yearmonth'] = pd.to_datetime(months_df['yearmonth'])

        #filter months_df with start_date and end_date, the contributor df is filtered in the visualizations
        months_df = months_df.set_index(months_df['yearmonth'])
        months_df = months_df.loc[start_date : end_date].reset_index(drop = True)

        #add quarters to months dataframe
        months_df['month'] = months_df['month'].astype(int)
        months_df['quarter'] = months_df.apply(lambda x: quarters(x['month'], x['year']), axis=1)
        months_df['quarter'] = pd.to_datetime(months_df['quarter'])



 

















        #create visualizations
        input_df = df

        #input_df = new_contributor_data_collection(repo_id=25158, num_contributions_required= required_contributions)
        #months_df = months_df_query(begin_date=start_date, end_date=end_date)

        repo_dict = {repo_id : input_df.loc[input_df['repo_id'] == repo_id].iloc[0]['repo_name']}   


        contributor_types = ['All', 'repeat', 'drive_by']
        ranks = [1,2]

        row_1 = []
        row_2 = []
        row_3 = []
        row_4 = []

        for rank in ranks:
            for contributor_type in contributor_types:
                #do not display these visualizations since drive-by's do not have second contributions, and the second contribution of a repeat contributor is the same thing as the all the second time contributors
                if (rank == 2 and contributor_type == 'drive_by') or (rank == 2 and contributor_type == 'repeat'):
                    continue

                #create a copy of contributor dataframe
                driver_df = input_df.copy()
                            
                #remove first time contributors before begin date, along with their second contribution
                mask = (driver_df['yearmonth'] < start_date)
                driver_df= driver_df[~driver_df['cntrb_id'].isin(driver_df.loc[mask]['cntrb_id'])]
                
                
                #create separate repeat_df that includes all repeat contributors
                #then any contributor that is not in the repeat_df is a drive-by contributor
                repeats_df = driver_df.copy()
                
                #discards rows other than the first and the row required to be a repeat contributor
                repeats_df = repeats_df.loc[repeats_df['rank'].isin([1,required_contributions])]

                #removes all the contributors that only have a first contirbution
                repeats_df = repeats_df[repeats_df['cntrb_id'].isin(repeats_df.loc[driver_df['rank'] == required_contributions]['cntrb_id'])]
                
                #create lists of 'created_at' times for the final required contribution and the first contribution
                repeat_list = repeats_df.loc[driver_df['rank'] == required_contributions]['created_at'].tolist()
                first_list = repeats_df.loc[driver_df['rank'] == 1]['created_at'].tolist()
             
                #only keep first time contributions, since those are the dates needed for visualization
                repeats_df = repeats_df.loc[driver_df['rank'] == 1]

                #create list of time differences between the final required contribution and the first contribution, and add it to the df
                differences = []
                for i in range(0, len(repeat_list)):
                    time_difference = repeat_list[i] - first_list[i]
                    total = time_difference.days * 86400 + time_difference.seconds
                    differences.append(total)
                repeats_df['differences'] = differences

                #remove contributions who made enough contributions, but not in a short enough time
                repeats_df = repeats_df.loc[repeats_df['differences'] <= required_time * 86400]
                
                
                if contributor_type == 'repeat':
                    driver_df = repeats_df
                    
                    caption = """This graph shows repeat contributors in the specified time period. Repeat contributors are contributors who have 
                    made {} or more contributions in {} days and their first contribution is in the specified time period. New contributors 
                    are individuals who make their first contribution in the specified time period."""
                    
                elif contributor_type == 'drive_by':

                    #create list of 'cntrb_ids' for repeat contributors
                    repeat_cntrb_ids = repeats_df['cntrb_id'].to_list()

                    #create df with all contributors other than the ones in the repeats_df
                    driver_df = driver_df.loc[~driver_df['cntrb_id'].isin(repeat_cntrb_ids)]
                 
                    #filter df so it only includes the first contribution
                    driver_df = driver_df.loc[driver_df['rank'] == 1]
                    
                    caption = """This graph shows drive by contributors in the specified time period. Drive by contributors are contributors who 
                    make less than the required {} contributions in {} days. New contributors are individuals who make their first contribution 
                    in the specified time period. Of course, then, “All drive-by’s are by definition first time contributors”. However, not all 
                    first time contributors are drive-by’s."""
                
                
                elif contributor_type == 'All':
                    if rank == 1:
                        #makes df with all first time contributors
                        driver_df = driver_df.loc[driver_df['rank'] == 1]
                        caption = """This graph shows all the first time contributors, whether they contribute once, or contribute multiple times. 
                        New contributors are individuals who make their first contribution in the specified time period."""
                        
                    if rank == 2:
                        #creates df with all second time contributors
                        driver_df = driver_df.loc[driver_df['rank'] == 2]
                        caption = """This graph shows the second contribution of all first time contributors in the specified time period."""
                        y_axis_label = 'Second Time Contributors'
                


                #filter by end_date, this is not done with the begin date filtering because a repeat contributor will look like drive-by if the second contribution is removed by end_date filtering
                mask = (driver_df['yearmonth'] < end_date)
                driver_df = driver_df.loc[mask]

                #adds all months to driver_df so the lists of dates will include all months and years    
                driver_df = pd.concat([driver_df, months_df])

                data = pd.DataFrame()
                if group_by == 'year': 

                    data['dates'] = driver_df[group_by].unique()

                    #new contributor counts for y-axis
                    data['new_contributor_counts'] = driver_df.groupby([group_by]).sum().reset_index()['new_contributors']

                    #used to format x-axis and title
                    group_by_format_string = "Year"

                elif group_by == 'quarter' or group_by == 'month':
                    
                    #set variables to group the data by quarter or month
                    if group_by == 'quarter':
                        date_column = 'quarter'
                        group_by_format_string = "Quarter"
                        
                    elif group_by == 'month':
                        date_column = 'yearmonth'
                        group_by_format_string = "Month"

                        
                    #modifies the driver_df[date_column] to be a string with year and month, then finds all the unique values   
                    data['dates'] = np.unique(np.datetime_as_string(driver_df[date_column], unit = 'M'))

                    
                    #new contributor counts for y-axis
                    data['new_contributor_counts'] = driver_df.groupby([date_column]).sum().reset_index()['new_contributors']


                #if the data set is large enough it will dynamically assign the width, if the data set is too small it will by default set to 870 pixel so the title fits
                if len(data['new_contributor_counts']) >= 15:
                    plot_width = 46 * len(data['new_contributor_counts'])
                else:
                    plot_width = 870 
                    
                #create a dict convert an integer number into a word
                #used to turn the rank into a word, so it is nicely displayed in the title
                numbers = ['Zero', 'First', 'Second']
                num_conversion_dict = {}
                for i in range(1, len(numbers)):
                    num_conversion_dict[i] = numbers[i]
                number =  '{}'.format(num_conversion_dict[rank])

                #define pot for bar chart
                p = figure(x_range=data['dates'], plot_height=400, plot_width = plot_width, title="Hello", #title.format(repo_dict[repo_id], contributor_type.capitalize(), number, group_by_format_string), 
                           y_range=(0, max(data['new_contributor_counts'])* 1.15), margin = (0, 0, 10, 0))

                
                
                p.vbar(x=data['dates'], top=data['new_contributor_counts'], width=0.8)

                source = ColumnDataSource(data=dict(dates=data['dates'], new_contributor_counts=data['new_contributor_counts']))


                #add contributor_count labels to chart
                p.add_layout(LabelSet(x='dates', y='new_contributor_counts', text='new_contributor_counts', y_offset=4,
                          text_font_size="13pt", text_color="black",
                          source=source, text_align='center'))

                p.xgrid.grid_line_color = None
                p.y_range.start = 0
                p.axis.minor_tick_line_color = None
                p.outline_line_color = None

                p.title.align = "center"
                p.title.text_font_size = "18px"



                p.yaxis.axis_label = 'Second Time Contributors' if rank == 2 else 'New Contributors'
                p.xaxis.axis_label = group_by_format_string 

                p.xaxis.axis_label_text_font_size = "18px"
                p.yaxis.axis_label_text_font_size = "16px"

                p.xaxis.major_label_text_font_size = "16px"
                p.xaxis.major_label_orientation = 45.0

                p.yaxis.major_label_text_font_size = "16px"

                plot = p
                
                #creates plot to hold caption 
                p = figure(width = plot_width, height=200, margin = (0, 0, 0, 0))

                p.add_layout(Label(
                x = 0, # Change to shift caption left or right
                y = 160, 
                x_units = 'screen',
                y_units = 'screen',
                text='{}'.format(caption.format(required_contributions, required_time)),
                text_font = 'times', # Use same font as paper
                text_font_size = '15pt',
                render_mode='css'
                ))
                p.outline_line_color = None

                caption_plot = p

                if rank == 1 and (contributor_type == 'All'  or contributor_type == 'repeat'):
                    row_1.append(plot)
                    row_2.append(caption_plot)
                elif rank == 2 or contributor_type == 'drive_by':
                    row_3.append(plot)
                    row_4.append(caption_plot)

        #puts plots together into a grid
        grid = gridplot([row_1, row_2, row_3, row_4])


        #output_file = 'images/' + 'new_contributors_stacked_bar' + '_' + contributor_type + '_' + group_by + '_' + repo_dict[repo_id] + '.png'


        #return grid

        #grid = vertical_bar_chart(repo_id=repo_id, start_date=start_date, end_date=end_date, group_by=group_by, required_contributions=required_contributions, required_time=required_time)
        print("Made it here")
        image = get_screenshot_as_png(grid, webdriver=webdriver)
        print("Made it here")

        #return json.dumps(json_item(grid, "myplot"))


        #return send_file(image, mimetype='application/json')

        #print(image)

        # set return headers
        #return Response(response=json.dumps(bokeh.embed.json_item(grid, "myplot")),
        #                mimecode='image/png',
        #                statuscode=200)
        #return json.dumps(json_item(p, "myplot"))

        #return send_file(filename=output_file, mimetype='application/json')

        #return json.dumps(bokeh.embed.json_item(grid, "myplot"))


        status = {
                'status': 'OK',
            }
        return Response(response=json.dumps(status),
                        status=200,
                        mimetype="application/json")



        #return Response(response=json.dumps(json_item(grid, "myplot"),
        #                        status=200,
        #                        mimetype=application/json))

    

