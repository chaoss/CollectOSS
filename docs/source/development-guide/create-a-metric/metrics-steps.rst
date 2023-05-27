Steps to Create a Metric API Endpoint
==========================================


Summary
---------------------------------------------------------------------------

There are many paths, but we usually follow something along these lines: 

1. What is the CHAOSS metric we want to develop? 
2. Sometimes, there are metrics endpoints that integrate, or visualize several metrics.
3. Determine what tables in the Augur Schema contain the data we need to develop this metric
4. Construct a very basic query that does the work of joining those tables in a minimal way so we have a "baseline query."
5. Refine the query so that it takes the standard inputs for a "standard metric" if that's what type it is; alternatively, look at non-standard metrics as they are defined in ``AUGUR_HOME/augur/routes``, or one of the visualization metrics in ``AUGUR_HOME/augur/routes/contributor.py``, ``AUGUR_HOME/augur/routes/pull_requests.py`` or ``AUGUR_HOME/augur/routes/nonstandard_metrics.py``. (This step is explained in the next section.)


Example Query 
---------------------------------------------------------------------

This is an example query to Get Us Started on a Labor Effort and Cost Endpoint.

1. What tables? 

.. code-block:: python 

   repo
   repo_group

If we look at the Augur Schema, we can see that effort and cost are contained in the ``repo_labor`` table. 

2. What might our initial query to explore building the endpoint be? 

.. code-block:: sql 

   SELECT C.repo_id,
	C.repo_name,
	programming_language,
	SUM ( estimated_labor_hours ) AS labor_hours,
	SUM ( estimated_labor_hours * 50 ) AS labor_cost,
	analysis_date 
	FROM
	(
		SELECT A
			.repo_id,
			b.repo_name,
			programming_language,
			SUM ( total_lines ) AS repo_total_lines,
			SUM ( code_lines ) AS repo_code_lines,
			SUM ( comment_lines ) AS repo_comment_lines,
			SUM ( blank_lines ) AS repo_blank_lines,
			AVG ( code_complexity ) AS repo_lang_avg_code_complexity,
			AVG ( code_complexity ) * SUM ( code_lines ) + 20 AS estimated_labor_hours,
			MAX ( A.rl_analysis_date ) AS analysis_date 
		FROM
			repo_labor A,
			repo b 
		WHERE
			A.repo_id = b.repo_id 
		GROUP BY
			A.repo_id,
			programming_language,
			repo_name 
		ORDER BY
			repo_name,
			A.repo_id,
			programming_language 
		) C 
	GROUP BY
		repo_id,
		repo_name,
		programming_language,
		C.analysis_date 
	ORDER BY
		repo_id,
		programming_language;

3. Over time, as CHAOSS develops a metric for labor investment, the way we calculate hours, and cost in this query will adapt to whatever the CHAOSS community determines is an apt formula.
4. We will fit this metric into one of the different types of metric API Endpoints discussed in the next section. 

.. note::

   Augur uses https://github.com/boyter/scc to calculate information contained in the ``labor_value`` table, which is populated by the ``value_worker`` tasks. 
