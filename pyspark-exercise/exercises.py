from session import get_spark
from pyspark.sql.functions import *

spark = get_spark()


def exercise_01():
    """
    Problem 1: DataFrame basics (select / filter / withColumn / when-otherwise)

    You're given an `orders` DataFrame:
        order_id | amount | status
        ---------|--------|--------
        1        | 150    | SUCCESS
        2        | 80     | SUCCESS
        3        | 30     | FAILED
        4        | 200    | SUCCESS
        5        | 60     | FAILED

    Tasks:
      1. Add a column `amount_tier`:
           - 'high'   if amount > 100
           - 'medium' if 50 <= amount <= 100
           - 'low'    if amount < 50
      2. Keep only rows where status == 'SUCCESS'.
      3. Return the resulting DataFrame, sorted by order_id.

    Expected output (as rows of order_id, amount, status, amount_tier):
        (1, 150, 'SUCCESS', 'high')
        (2, 80,  'SUCCESS', 'medium')
        (4, 200, 'SUCCESS', 'high')

    Useful DataFrame methods / built-in functions:
        - df.withColumns({colName: expr, ...})   adds/replaces columns from a dict, single projection
                                                  (default to this over chained .withColumn() calls,
                                                  even for just one column here — it's the pattern
                                                  that scales, so build the habit now)
        - col()                          reference a column by name (from pyspark.sql.functions)
        - when() / otherwise()           conditional column logic, like CASE WHEN (from pyspark.sql.functions)
        - df.filter() / df.where()       row filtering
        - df.orderBy() / df.sort()       sorting

    Note: unlike pandas (eager — call order affects perf directly), Spark is lazy.
    Catalyst builds a plan from your whole chain and reorders operations itself
    (e.g. pushing filters below projections) before anything runs. Write
    withColumns/filter/orderBy in whatever order reads clearest.
    """
    data = [
        (1, 150, "SUCCESS"),
        (2, 80, "SUCCESS"),
        (3, 30, "FAILED"),
        (4, 200, "SUCCESS"),
        (5, 60, "FAILED"),
    ]
    df = spark.createDataFrame(data, ["order_id", "amount", "status"])

    # TODO: implement here
    df_final = df.withColumns({"amount_tier":when(col("amount") > 100, "high").when((col("amount")>= 50) & (col("amount") <=100), "medium").otherwise("low")})\
        .filter(upper(col('status')) == 'SUCCESS')\
        .orderBy([col("order_id"),col("amount_tier")],ascending=[True,True])
    result = df_final

    return result


def exercise_02():
    """
    Problem 2: Aggregations (groupBy / agg, post-aggregation filtering)

    You're given a `sales` DataFrame:
        department | employee | amount
        -----------|----------|-------
        Sales      | Alice    | 100
        Sales      | Bob      | 150
        Sales      | Carol    | 50
        Eng        | Dave     | 300
        Eng        | Eve      | 200
        HR         | Frank    | 20

    Tasks:
      1. Group by `department`, computing for each:
           - total_amount  (sum of amount)
           - avg_amount    (average amount)
           - emp_count     (count of employees)
      2. Keep only departments where total_amount > 200 ("having" equivalent —
         filtering applied after the aggregation, not before).
      3. Return the result sorted by total_amount, descending.

    Expected output (department, total_amount, avg_amount, emp_count):
        ('Eng',   500, 250.0, 2)
        ('Sales', 300, 100.0, 3)
    (HR is filtered out: total_amount = 20, not > 200)

    Useful DataFrame methods / built-in functions:
        - df.groupBy(colName)
              groups rows by one or more columns.
              single column:    df.groupBy("department")
              multiple columns: df.groupBy("department", "region")

        - .agg(*exprs)
              one or more aggregations per group, each given a flat output
              column name directly via .alias() — unlike pandas' groupby().agg()
              with a dict/list, which produces MultiIndex columns you then have
              to flatten, Spark's agg() output is already flat.
                  df.groupBy("department").agg(
                      sum("amount").alias("total_amount"),
                      avg("amount").alias("avg_amount"),
                      count("employee").alias("emp_count"),
                  )

        - sum() / avg() / count()   (from pyspark.sql.functions)
              aggregation functions used inside .agg(); each takes a column name
              or Column expression.
                  sum("amount")           # sums a single column
                  count("employee")       # counts non-null employee values per group
                  count("*")              # counts all rows per group, nulls included

        - df.filter() / df.where()
              applied AFTER .agg() = the "having" equivalent (filters on the
              aggregated columns, not the raw rows).
                  df.groupBy("department").agg(sum("amount").alias("total_amount")) \\
                      .filter(col("total_amount") > 200)
              multi-condition:
                  .filter((col("total_amount") > 200) & (col("emp_count") >= 2))

        - df.orderBy(...)  /  df.sort(...)
              descending sort needs .desc() on the Column (plain column name
              defaults to ascending).
              single column:
                  df.orderBy(col("total_amount").desc())
              multiple columns, mixed direction:
                  df.orderBy(col("total_amount").desc(), col("department").asc())
    """
    data = [
        ("Sales", "Alice", 100),
        ("Sales", "Bob", 150),
        ("Sales", "Carol", 50),
        ("Eng", "Dave", 300),
        ("Eng", "Eve", 200),
        ("HR", "Frank", 20),
    ]
    df = spark.createDataFrame(data, ["department", "employee", "amount"])

    # TODO: implement here
    df_grouped = df.groupBy("department", "employee").agg(sum("amount").alias("total_amount"),avg("amount").alias("avg_amount"),countDistinct("employee").alias("emp_count"))\
        .filter(col("total_amount") > 200)\
        .orderBy([col("total_amount"),col("department")],ascending=[False,True])
    result = df_grouped

    return result


def exercise_03():
    """
    Problem 3: Joins (inner / left / self-join / semi / anti / broadcast)

    You're given two DataFrames:

        employees
        emp_id | name  | dept_id | manager_id
        -------|-------|---------|------------
        1      | Alice | 10      | NULL
        2      | Bob   | 10      | 1
        3      | Carol | 20      | 1
        4      | Dave  | 30      | 2
        5      | Eve   | NULL    | 2

        departments
        dept_id | dept_name
        --------|------------
        10      | Engineering
        20      | Sales
        40      | Marketing

    Tasks:
      1. Inner join employees to departments on dept_id. Return (name, dept_name).
         Only matched rows survive (Eve has no dept_id, Marketing has no employees
         -- both drop out).
      2. Left join employees to departments on dept_id (employees as the left side).
         Return (name, dept_name). Eve is now kept, with dept_name = NULL.
      3. Self-join employees to itself to resolve each employee's manager's name:
         join employees.manager_id to a second copy of employees on emp_id.
         Return (employee_name, manager_name). Alice has no manager -> manager_name
         = NULL.

    Expected output:
      Task 1 (inner):
        ('Alice', 'Engineering')
        ('Bob',   'Engineering')
        ('Carol', 'Sales')
      Task 2 (left):
        same 3 rows as Task 1, plus:
        ('Eve', None)
      Task 3 (self-join):
        ('Alice', None)
        ('Bob',   'Alice')
        ('Carol', 'Alice')
        ('Dave',  'Bob')
        ('Eve',   'Bob')

    Useful DataFrame methods / built-in functions:
        - df1.join(df2, on=..., how=...)
              the general join call. `on` can be a single column name, a list of
              column names (when both sides share the name), or a Column
              expression (when column names differ or you need aliases).
              single shared column:
                  employees.join(departments, on="dept_id", how="inner")
              multiple shared columns:
                  df1.join(df2, on=["dept_id", "region_id"], how="inner")
              differing column names / explicit expression:
                  employees.join(
                      departments,
                      employees["dept_id"] == departments["dept_id"],
                      how="left",
                  )

        - how="inner" / "left" / "right" / "full"
              standard join types, same meaning as SQL.
                  employees.join(departments, "dept_id", "left")

        - self-join (join a DataFrame to itself)
              give each side an alias so column references stay unambiguous --
              referencing employees["name"] twice would be undefined otherwise.
                  emp = employees.alias("emp")
                  mgr = employees.alias("mgr")
                  emp.join(mgr, col("emp.manager_id") == col("mgr.emp_id"), "left") \\
                      .select(col("emp.name").alias("employee_name"),
                              col("mgr.name").alias("manager_name"))

        - how="left_semi" / "left_anti"
              filter one DataFrame based on presence/absence of a match in another,
              without pulling in any columns from the right side (like a WHERE
              EXISTS / WHERE NOT EXISTS). Useful for "departments with (out) any
              employees" type questions.
                  departments.join(employees, "dept_id", "left_semi")   # has employees
                  departments.join(employees, "dept_id", "left_anti")   # has no employees

        - broadcast(df)   (from pyspark.sql.functions)
              hints Spark to send the smaller DataFrame to every executor instead
              of shuffling both sides across the cluster -- worth mentioning out
              loud in an interview when joining a small lookup table (like
              `departments` here) against a much larger one.
                  from pyspark.sql.functions import broadcast
                  employees.join(broadcast(departments), "dept_id", "inner")
              often not even required explicitly -- Spark auto-broadcasts any side
              estimated under spark.sql.autoBroadcastJoinThreshold (default 10MB)
              on its own. The hint mainly matters once Spark's size estimate is
              stale/unavailable (e.g. after several chained transformations), or
              when you want to force it regardless of the estimate. Confirm what
              actually happened via .explain() -> look for BroadcastHashJoin vs
              SortMergeJoin in the physical plan.

    Gotchas actually hit while solving this exercise (self-join aliasing):
        - `df['col']` won't work unless `df` itself is a variable holding a real
          DataFrame. `employees.alias('mgr')` does NOT create a Python variable
          named `mgr` -- you must assign it: `mgr = employees.alias('mgr')`.
          Referencing an unassigned alias name raises NameError, not anything
          Spark-specific.

        - Aliasing only ONE side of a self-join still fails. If `employees` is
          used bare (unaliased) anywhere in the join/select while `managers =
          employees.alias('managers')` is the other side, Spark still can't
          resolve columns and raises AnalysisException: "Column ... are
          ambiguous ... some of these Datasets are the same." Both sides need
          their own alias, including the one that "feels like" the base table.

        - Even aliasing BOTH sides can still fail with the same ambiguous-column
          error. Root cause: `.alias()` on a DataFrame only adds a name
          qualifier to the logical plan -- it does NOT regenerate the
          underlying column expression IDs (the `#0L`-style suffix Spark shows
          in error messages). If both aliased copies trace back to the same
          original DataFrame object, their columns can still carry identical
          expression IDs under the hood, so qualifier-based disambiguation
          isn't guaranteed to work.

        - The reliable fix: rename columns to unique names via `.select(col(...)
          .alias(...))` BEFORE joining, instead of relying on DataFrame-level
          `.alias()` + qualified names. `.alias()` called on a *Column* (inside
          select) creates a genuinely new expression with a fresh ID, so there's
          nothing left to disambiguate:
              managers = employees.select(
                  col("emp_id").alias("mgr_emp_id"),
                  col("name").alias("mgr_name"),
              )
              employees.join(managers, employees["manager_id"] == managers["mgr_emp_id"], "left") \\
                  .select(col("name"), col("mgr_name"))

        - `col("alias.column")` (string-qualified name) only resolves correctly
          when that exact SubqueryAlias still directly wraps a column of that
          exact unqualified name in the CURRENT plan. Any `.select()`/rename
          in between breaks it silently-ish (AnalysisException:
          UNRESOLVED_COLUMN), because the new projected columns aren't
          re-wrapped in the alias. `df['col']` / `df.col` bracket-or-dot access
          resolves directly against that DataFrame object's own schema instead
          and isn't affected by this.

        - There is no `.as()` method in PySpark -- `as` is a reserved Python
          keyword, so `df.as(...)` is a SyntaxError. `.alias()` IS the Python
          binding for Scala's `Dataset.as()`; the error message mentioning
          `Dataset.as` is just reused verbatim from the JVM side.

        - `from pyspark.sql.functions import *` is only legal at module level.
          Writing it inside a function body raises SyntaxError: "import * only
          allowed at module level" (Python can't statically resolve a
          function's local names if a wildcard import is inside it).
    """
    employees_data = [
        (1, "Alice", 10, None),
        (2, "Bob", 10, 1),
        (3, "Carol", 20, 1),
        (4, "Dave", 30, 2),
        (5, "Eve", None, 2),
    ]
    employees = spark.createDataFrame(
        employees_data, ["emp_id", "name", "dept_id", "manager_id"]
    )

    departments_data = [
        (10, "Engineering"),
        (20, "Sales"),
        (40, "Marketing"),
    ]
    departments = spark.createDataFrame(departments_data, ["dept_id", "dept_name"])

    # TODO: implement here
    
    #task1 = employees.join(broadcast(departments), on=employees['dept_id'] == departments['dept_id'], how='inner')
    task2 = departments.join(employees, on=employees['dept_id'] == departments['dept_id'], how='left')
    managers = employees.alias('managers').select(col('emp_id').alias('manager_id'), col('name').alias('manager_name'))
    employees = employees.alias('employees')
    task3 = employees.join(managers, on=(employees['manager_id'] > managers['manager_id']), how='left').select(col('employees.name'), col('manager_name'))
    result = task3

    return result


def exercise_04():
    """
    Problem 4: Window functions (row_number / rank / lag / rolling / cumulative)

    You're given an `employee_sales` DataFrame:
        employee | sale_date  | amount
        ---------|------------|-------
        Alice    | 2024-01-01 | 100
        Alice    | 2024-01-02 | 150
        Alice    | 2024-01-03 | 120
        Bob      | 2024-01-01 | 300
        Bob      | 2024-01-02 | 250
        Bob      | 2024-01-03 | 400
        Carol    | 2024-01-01 | 50
        Carol    | 2024-01-02 | 80

    Tasks (all partitioned per employee -- each employee's window is independent):
      1. `sale_rank`: rank each employee's own sales from highest to lowest amount
         (partition by employee, order by amount descending). Ties would share a
         rank (not exercised by this data, but know rank() vs dense_rank()).
      2. `prev_amount`: the employee's previous day's amount, ordered by sale_date
         (first day per employee = NULL, no previous row).
      3. `running_total`: cumulative sum of amount per employee, ordered by
         sale_date.
      4. `rolling_avg_2`: rolling average of the current day + previous day's
         amount per employee, ordered by sale_date (first day per employee has
         no previous row, so the window just contains itself).

    Expected output (employee, sale_date, amount, sale_rank, prev_amount, running_total, rolling_avg_2):
        Alice 01-01 100  3  NULL  100  100.0
        Alice 01-02 150  1  100   250  125.0
        Alice 01-03 120  2  150   370  135.0
        Bob   01-01 300  2  NULL  300  300.0
        Bob   01-02 250  3  300   550  275.0
        Bob   01-03 400  1  250   950  325.0
        Carol 01-01 50   2  NULL  50   50.0
        Carol 01-02 80   1  50    130  65.0

    Useful DataFrame methods / built-in functions:
        - Window.partitionBy(...).orderBy(...)
              defines a window spec: which rows are "peers" (partitionBy) and how
              they're ordered within each partition (orderBy). Every window
              function below needs one of these passed to .over().
                  from pyspark.sql.window import Window
                  w = Window.partitionBy("employee").orderBy("sale_date")
              multiple partition columns:
                  Window.partitionBy("dept", "employee").orderBy("sale_date")

        - row_number() / rank() / dense_rank()   .over(windowSpec)
              row_number(): always unique & sequential (1,2,3,...), even on ties.
              rank(): ties share a rank, next rank SKIPS (1,1,3).
              dense_rank(): ties share a rank, next rank does NOT skip (1,1,2).
                  df.withColumn(
                      "sale_rank",
                      rank().over(Window.partitionBy("employee").orderBy(col("amount").desc())),
                  )

        - lag(colName, offset=1) / lead(colName, offset=1)   .over(windowSpec)
              look at a previous/next row's value within the same partition,
              per the window's orderBy. This is the direct equivalent of
              pandas' groupby()["col"].shift().
                  df.withColumn(
                      "prev_amount",
                      lag("amount", 1).over(Window.partitionBy("employee").orderBy("sale_date")),
                  )

        - windowSpec.rowsBetween(start, end)
              restricts a window function to a sliding range of rows relative to
              the current row -- this is what makes running totals / rolling
              averages possible (direct equivalent of pandas' .cumsum() and
              .rolling(window=n).mean()). Window.unboundedPreceding /
              Window.currentRow are special bounds; plain ints are relative
              row offsets from the current row.
                  running_w = Window.partitionBy("employee").orderBy("sale_date") \\
                      .rowsBetween(Window.unboundedPreceding, Window.currentRow)
                  df.withColumn("running_total", sum("amount").over(running_w))

                  rolling_w = Window.partitionBy("employee").orderBy("sale_date").rowsBetween(-1, 0)
                  df.withColumn("rolling_avg_2", avg("amount").over(rolling_w))
    """
    from pyspark.sql.window import Window

    data = [
        ("Alice", "2024-01-01", 100),
        ("Alice", "2024-01-02", 150),
        ("Alice", "2024-01-03", 120),
        ("Bob", "2024-01-01", 300),
        ("Bob", "2024-01-02", 250),
        ("Bob", "2024-01-03", 400),
        ("Carol", "2024-01-01", 50),
        ("Carol", "2024-01-02", 80),
    ]
    df = spark.createDataFrame(data, ["employee", "sale_date", "amount"])

    # TODO: implement here
    task1 = df.withColumns({'sale_rank':rank().over(Window.partitionBy('employee').orderBy(col('amount').desc()))})
    task2 = df.withColumns({'amount_lag_1':lag('amount',1).over(Window.partitionBy('employee').orderBy('sale_date'))}).orderBy(['employee','sale_date'],ascending=[True,True])
    task3 = df.withColumns({'running_total':sum('amount').over(Window.partitionBy('employee').orderBy('sale_date').rowsBetween(Window.unboundedPreceding, Window.currentRow))})\
        .orderBy(['employee','sale_date'],ascending=[True,True])
    task4 = df.withColumns({'rolling_avg_2':avg('amount').over(Window.partitionBy('employee').orderBy('sale_date').rowsBetween(-1,0))})\
        .orderBy(['employee','sale_date'],ascending=[True,True])
    result = task4

    return result


def exercise_05():
    """
    Problem 5: String / date handling (to_date, date_format, datediff, split, regexp_extract)

    You're given a `user_events` DataFrame:
        user_id | login_ts            | email
        --------|---------------------|------------------------
        1       | 2024-03-01 08:15:00 | alice.smith@example.com
        2       | 2024-03-03 23:50:00 | bob99@example.com
        3       | 2024-03-05 12:00:00 | carol.jones@example.com

    Tasks:
      1. `login_date`: the date-only portion of `login_ts` (as an actual DateType,
         not just a truncated string).
      2. `days_since_launch`: number of days between `login_date` and a fixed
         launch date of '2024-03-01'.
      3. `email_user`: the part of `email` before the '@'.
      4. `email_domain`: the part of `email` after the '@'.

    Expected output (user_id, login_date, days_since_launch, email_user, email_domain):
        1  2024-03-01  0  'alice.smith'  'example.com'
        2  2024-03-03  2  'bob99'        'example.com'
        3  2024-03-05  4  'carol.jones'  'example.com'

    Useful DataFrame methods / built-in functions:
        - to_date(col, format=None)
              parses a string/timestamp column into an actual DateType column
              (not just reformatted text -- this matters for datediff/date math
              to work correctly).
                  to_date(col("login_ts"))                          # infers default timestamp format
                  to_date(col("login_ts"), "yyyy-MM-dd HH:mm:ss")    # explicit format, safer if inference is ambiguous

        - date_format(col, format)
              formats a date/timestamp column back into a display string per a
              pattern -- the inverse direction of to_date.
                  date_format(col("login_date"), "yyyy-MM-dd")
                  date_format(col("login_date"), "MMM dd, yyyy")     # e.g. "Mar 01, 2024"

        - datediff(end, start)
              integer number of days between two dates/timestamps (end - start).
              single fixed reference date:
                  datediff(col("login_date"), to_date(lit("2024-03-01")))
              two columns:
                  datediff(col("end_date"), col("start_date"))

        - split(str, pattern)
              splits a string column into an array by a regex pattern; pull out
              a piece with .getItem(i) or bracket indexing.
                  split(col("email"), "@")                # array column: ["alice.smith", "example.com"]
                  split(col("email"), "@").getItem(0)      # "alice.smith"
                  split(col("email"), "@")[1]              # "example.com" -- equivalent to getItem(1)

        - regexp_extract(str, pattern, groupIdx)
              pulls out one regex capture group directly as a string column, no
              array/indexing needed -- often cleaner than split() when the piece
              you want isn't just "everything before/after one delimiter".
                  regexp_extract(col("email"), r"^([^@]+)@", 1)   # everything before @
                  regexp_extract(col("email"), r"@(.+)$", 1)      # everything after @

    Gotchas actually hit while solving this exercise (bare strings as arguments):
        - A bare Python string passed to a function parameter that represents
          "the column to operate on" is auto-converted to `col(that_string)` --
          i.e. Spark treats it as a COLUMN NAME LOOKUP, not a literal value.
          `to_date('2024-03-01')` raised AnalysisException:
          UNRESOLVED_COLUMN, because '2024-03-01' isn't an actual column name
          in the DataFrame -- Spark tried to resolve it as one and failed.
          Fix: wrap literal values explicitly: `to_date(lit('2024-03-01'))`.

        - The SAME rule is why `split('email', '@')` worked fine with no error,
          even though it also passed a bare string as the first argument. Not a
          different rule for split() -- 'email' just happens to genuinely be a
          real column name in this DataFrame, so Spark resolved it exactly as
          `col('email')` would have. Same mechanism, opposite outcome, purely
          because one string coincidentally matched a real column name and the
          other didn't.

        - This makes bare-string args a silent trap, not just an occasionally
          inconvenient one: if a column ever happened to be named the same as
          an intended literal value, the bare-string form would quietly
          resolve to that column instead of erroring -- zero warning, wrong
          result. Best practice: always be explicit -- `col(...)` when
          referencing an existing column, `lit(...)` when passing a literal
          value -- rather than relying on the auto-conversion even when it
          happens to work.

        - Note the SECOND argument in both cases above (`'@'` for split's
          delimiter, the format string for to_date) is NOT column-like and is
          always taken as a plain literal/format string -- only "the column to
          operate on" parameter gets the auto-lookup-by-name treatment.
    """
    data = [
        (1, "2024-03-01 08:15:00", "alice.smith@example.com"),
        (2, "2024-03-03 23:50:00", "bob99@example.com"),
        (3, "2024-03-05 12:00:00", "carol.jones@example.com"),
    ]
    df = spark.createDataFrame(data, ["user_id", "login_ts", "email"])

    # TODO: implement here
    df_final = df.withColumns({'login_date':to_date(col('login_ts')),'days_since_launch':datediff(col('login_date'),to_date(lit('2024-03-01')))
                               ,'email_user':split(col('email'),'@').getItem(0)
                               ,'email_domain':split('email','@').getItem(1)                              
                               })
    result = df_final

    return result


def exercise_06():
    """
    Problem 6: Arrays (explode, array_contains, collect_list / collect_set)

    You're given a `users_pages` DataFrame, where each user follows a list of
    pages (this is the PySpark-native version of the users_pages/explode
    pattern from pandas-exercise.py -- same idea, array column instead of a
    Python list-of-dicts):
        user_id | page_ids
        --------|-----------
        1       | [21, 25]
        2       | [25, 23, 24]
        3       | [21]

    Tasks:
      1. `exploded`: one row per (user_id, page_id) pair -- flatten the
         page_ids array so each element becomes its own row.
      2. `follows_25`: filter the ORIGINAL (non-exploded) DataFrame to only
         users whose page_ids array contains 25 -- without exploding first.
      3. `page_to_users`: starting from the exploded form, group by page_id
         and collect the set of user_ids who follow each page (an inverted
         index -- the reverse mapping of the original data).

    Expected output:
      Task 1 (exploded), 6 rows:
        (1, 21), (1, 25), (2, 25), (2, 23), (2, 24), (3, 21)
      Task 2 (follows_25):
        user_id 1 and user_id 2 (their page_ids arrays contain 25; user 3's
        does not)
      Task 3 (page_to_users), order of array elements not guaranteed:
        21 -> {1, 3}
        25 -> {1, 2}
        23 -> {2}
        24 -> {2}

    Useful DataFrame methods / built-in functions:
        - explode(col)
              turns an array column into one row per element -- other columns
              are duplicated across the exploded rows. This is a column
              function used inside select()/withColumn(), NOT a DataFrame
              method -- unlike pandas' df.explode('col'), which IS a
              DataFrame-level method. Same underlying idea (one row per
              element), different call shape.
                  df.select("user_id", explode(col("page_ids")).alias("page_id"))
              exploding two parallel arrays together, aligned by position
              (zip first, then explode the zipped struct):
                  df.select("user_id", explode(arrays_zip(col("page_ids"), col("weights"))).alias("zipped"))

        - array_contains(col, value)
              boolean check for whether an array column contains a given
              value -- useful as a filter without exploding first.
                  df.filter(array_contains(col("page_ids"), 25))
              as a derived column instead of a filter:
                  df.withColumn("follows_25", array_contains(col("page_ids"), 25))

        - collect_list(col) / collect_set(col)   (used inside .agg())
              aggregate values within a group back INTO an array -- the
              reverse of explode(). collect_list keeps duplicates and
              preserves no guaranteed order; collect_set de-duplicates.
              This is the real-array-type counterpart of what you did
              manually in pandas with `.astype(str).groupby().agg(','.join)`
              to re-collapse rows into a delimited string -- PySpark keeps it
              as an actual array, no join/split-string round-trip needed.
                  df.groupBy("page_id").agg(collect_set("user_id").alias("followers"))
              round-tripping back to the original shape after an explode:
                  df.groupBy("user_id").agg(collect_list("page_id").alias("page_ids"))
    """
    data = [
        (1, [21, 25]),
        (2, [25, 23, 24]),
        (3, [21]),
    ]
    df = spark.createDataFrame(data, ["user_id", "page_ids"])

    # TODO: implement here
    df_exploded = df.withColumns({'follows_25':array_contains(col('page_ids'),25)}).select('user_id','follows_25',explode(col('page_ids')).alias('page_id'))
    df_final = df_exploded.groupBy('page_id').agg(collect_set('user_id').alias('list_of_users')).orderBy(['page_id'],ascending=[True])
    result = df_final

    return result


def exercise_07():
    """
    Problem 7: Spark SQL (temp views, spark.sql(), HAVING, window functions in SQL)

    Same `sales` DataFrame as exercise 2:
        department | employee | amount
        -----------|----------|-------
        Sales      | Alice    | 100
        Sales      | Bob      | 150
        Sales      | Carol    | 50
        Eng        | Dave     | 300
        Eng        | Eve      | 200
        HR         | Frank    | 20

    Tasks:
      1. Register `df` as a temp view named "sales".
      2. Using `spark.sql(...)`, reproduce exercise 2's result via SQL instead
         of the DataFrame API: total_amount / avg_amount / emp_count per
         department, HAVING total_amount > 200, ordered by total_amount desc.
      3. Using `spark.sql(...)`, reproduce exercise 4's ranking pattern via SQL:
         rank each employee's amount within their department, highest first
         (RANK() OVER (PARTITION BY ... ORDER BY ... DESC)).

    Expected output:
      Task 2 (same numbers as exercise 2):
        ('Eng',   500, 250.0, 2)
        ('Sales', 300, 100.0, 3)
      Task 3 (department, employee, amount, dept_rank):
        Eng   Dave  300  1
        Eng   Eve   200  2
        Sales Bob   150  1
        Sales Alice 100  2
        Sales Carol 50   3

    Useful DataFrame methods / built-in functions:
        - df.createOrReplaceTempView(name)
              registers a DataFrame as a queryable table name for the lifetime
              of the SparkSession -- lets you run raw SQL strings against it.
                  df.createOrReplaceTempView("sales")

        - spark.sql(query_string)
              runs a SQL string and returns a DataFrame, exactly like any
              DataFrame API result -- you can keep chaining .filter()/.show()
              etc. on it, or feed it into more DataFrame API calls.
                  spark.sql("SELECT department, SUM(amount) AS total_amount FROM sales GROUP BY department")

        - GROUP BY ... HAVING ...
              SQL's native post-aggregation filter -- the direct SQL spelling
              of the DataFrame API's .filter() applied after .agg().
                  spark.sql('''
                      SELECT department,
                             SUM(amount) AS total_amount,
                             AVG(amount) AS avg_amount,
                             COUNT(employee) AS emp_count
                      FROM sales
                      GROUP BY department
                      HAVING SUM(amount) > 200
                      ORDER BY total_amount DESC
                  ''')

        - window functions in SQL:  <func>() OVER (PARTITION BY ... ORDER BY ...)
              same concept as exercise 4's Window.partitionBy().orderBy(), just
              SQL syntax instead of the DataFrame API.
                  spark.sql('''
                      SELECT department, employee, amount,
                             RANK() OVER (PARTITION BY department ORDER BY amount DESC) AS dept_rank
                      FROM sales
                  ''')
              multiple partition columns work the same way as the DataFrame API:
                  PARTITION BY department, region ORDER BY amount DESC
    """
    data = [
        ("Sales", "Alice", 100),
        ("Sales", "Bob", 150),
        ("Sales", "Carol", 50),
        ("Eng", "Dave", 300),
        ("Eng", "Eve", 200),
        ("HR", "Frank", 20),
    ]
    df = spark.createDataFrame(data, ["department", "employee", "amount"])

    # TODO: implement here
    df.createOrReplaceTempView('sales')
    df_department = spark.sql('''
                         select department,sum(amount) as total_amount,avg(amount) as avg_amount,count(employee) as emp_count
                         from sales
                         group by 1
                         having total_amount > 200
                         order by total_amount desc
                         ''')
    df_department_employees = spark.sql('''
                                        select department,employee
                                            ,rank() over(partition by department order by amount desc) as with_dept_rank
                                        ,sum(amount) over(partition by department order by employee rows between unbounded preceding and current row) as running_total
                                        from sales
                                        ''')
    result = df_department_employees

    return result


def exercise_08():
    """
    Problem 8: Conceptual/performance -- explain(), cache/persist, reading a physical plan

    This exercise is different in shape from the others: it's not about
    producing a specific output, it's about reading and controlling what Spark
    actually does at runtime. Reuses the `employees`/`departments` DataFrames
    from exercise 3 and the `sales` DataFrame from exercise 2.

    Tasks:
      1. Build `joined = employees.join(departments, "dept_id", "inner")` and
         call `joined.explain()`. Find the join strategy in the printed
         physical plan -- look for `BroadcastHashJoin` vs `SortMergeJoin`, and
         `BroadcastExchange`/`Exchange` (an `Exchange` node is a shuffle).
         `departments` is tiny, so expect Spark to have auto-broadcast it
         (see exercise 3's broadcast notes) -- confirm that's actually what
         happened rather than assuming it.
      2. Build the same join again but wrapped in `broadcast(departments)`
         explicitly, call `.explain()` again, and compare -- does the plan
         actually change, or was Spark already doing this on its own?
      3. Take the `sales` DataFrame, `.cache()` it, then trigger two separate
         actions on it (e.g. `.count()` then `.show()`). Conceptually: without
         caching, each action re-executes the whole lazy plan from scratch
         from the original source; `.cache()` materializes the result after
         the first action so the second one reuses it instead of recomputing.
         Finish with `.unpersist()` to release it explicitly.

    There's no single "expected output" table here -- the goal is being able
    to read `.explain()` output and explain out loud what caching buys you
    and when it's NOT worth it (a DataFrame used only once gains nothing from
    caching -- it's pure overhead in that case).

    Useful DataFrame methods:
        - df.explain()                    prints the physical plan (default: just the physical plan)
          df.explain(True)                prints parsed/analyzed/optimized/physical plans, all four stages
          df.explain("formatted")         a more readable, sectioned version of the physical plan

        - what to look for in the output:
              Exchange              -- a shuffle is happening here (expensive: network + disk)
              BroadcastExchange     -- Spark is broadcasting a side instead of shuffling it
              BroadcastHashJoin     -- the fast join strategy (no shuffle needed for the join itself)
              SortMergeJoin         -- the shuffle-based join strategy (both sides get shuffled + sorted)
              HashAggregate         -- the aggregation strategy for groupBy().agg()

        - df.cache()  /  df.persist(storageLevel)
              cache() is shorthand for persist(StorageLevel.MEMORY_AND_DISK) --
              marks a DataFrame to be materialized and kept (in memory, spilling
              to disk if it doesn't fit) after its first action, instead of
              being recomputed from scratch on every subsequent action.
                  sales_cached = sales.cache()
                  sales_cached.count()   # first action: computes AND caches
                  sales_cached.show()    # second action: reuses the cached result

        - df.unpersist()
              explicitly releases a cached/persisted DataFrame from
              memory/disk. Good practice once you're done reusing it,
              especially in a long-running job with many cached DataFrames.
    """
    employees_data = [
        (1, "Alice", 10, None),
        (2, "Bob", 10, 1),
        (3, "Carol", 20, 1),
        (4, "Dave", 30, 2),
        (5, "Eve", None, 2),
    ]
    employees = spark.createDataFrame(
        employees_data, ["emp_id", "name", "dept_id", "manager_id"]
    )

    departments_data = [
        (10, "Engineering"),
        (20, "Sales"),
        (40, "Marketing"),
    ]
    departments = spark.createDataFrame(departments_data, ["dept_id", "dept_name"])

    sales_data = [
        ("Sales", "Alice", 100),
        ("Sales", "Bob", 150),
        ("Sales", "Carol", 50),
        ("Eng", "Dave", 300),
        ("Eng", "Eve", 200),
        ("HR", "Frank", 20),
    ]
    sales = spark.createDataFrame(sales_data, ["department", "employee", "amount"])

    # TODO: implement here
    joined = employees.join(departments, on=(employees['dept_id'] == departments['dept_id']), how='inner')
    joined.explain()
    result = joined

    return result


def exercise_09():
    """
    Problem 9: Capstone -- top-N per group (join + aggregation + window function)

    Try to timebox this one to ~20-25 minutes, like a real live-coding round.

    You're given two DataFrames:

        customers
        customer_id | name  | region
        ------------|-------|-------
        1           | Alice | West
        2           | Bob   | West
        3           | Carol | East
        4           | Dave  | East
        5           | Eve   | West

        orders
        order_id | customer_id | order_date | amount | status
        ---------|-------------|------------|--------|----------
        101      | 1           | 2024-01-05 | 200    | COMPLETED
        102      | 1           | 2024-02-10 | 150    | COMPLETED
        103      | 2           | 2024-01-20 | 500    | COMPLETED
        104      | 2           | 2024-03-01 | 100    | CANCELLED
        105      | 3           | 2024-01-15 | 300    | COMPLETED
        106      | 4           | 2024-02-01 | 700    | COMPLETED
        107      | 4           | 2024-02-20 | 50     | COMPLETED
        108      | 5           | 2024-01-10 | 400    | COMPLETED
        109      | 5           | 2024-03-15 | 600    | COMPLETED

    Task: find the top 2 customers by total spend, per region. Only count
    COMPLETED orders (CANCELLED orders -- like order 104 -- don't count
    toward spend at all).

    Steps this naturally breaks into (all techniques from earlier exercises):
      1. Filter orders to COMPLETED only.
      2. Join to customers to get each order's region.
      3. Group by customer (and region), computing total_spend (sum) and
         order_count (count).
      4. Rank customers within their region by total_spend, descending
         (window function).
      5. Keep only rank <= 2 per region.

    Expected output (region, name, total_spend, order_count, region_rank):
        East  Dave  750   2   1
        East  Carol 300   1   2
        West  Eve   1000  2   1
        West  Bob   500   1   2
    (Alice is excluded -- she's rank 3 in West, behind Eve and Bob.)

    Useful DataFrame methods / built-in functions:
        - this problem doesn't need any function you haven't already used in
          exercises 1-4 -- join(), groupBy().agg(), Window.partitionBy().orderBy(),
          rank().over(...), and filter(). The exercise is really about chaining
          them together correctly, not learning new syntax.

        - one genuinely new wrinkle worth knowing: filtering on a window
          function's result (step 5) is straightforward in the DataFrame API --
          just two separate chained calls, since withColumn() and filter() are
          independent lazy steps:
              ranked = grouped.withColumn(
                  "region_rank", rank().over(Window.partitionBy("region").orderBy(col("total_spend").desc()))
              )
              result = ranked.filter(col("region_rank") <= 2)
          In SQL, this ISN'T directly possible in the same SELECT -- window
          functions logically execute after WHERE, so `WHERE region_rank <= 2`
          in the same query as the window function definition is invalid.
          SQL needs a subquery or CTE instead:
              WITH ranked AS (
                  SELECT *, RANK() OVER (PARTITION BY region ORDER BY total_spend DESC) AS region_rank
                  FROM grouped
              )
              SELECT * FROM ranked WHERE region_rank <= 2
          Good one to know explicitly: the DataFrame API sidesteps a
          restriction that SQL forces you to work around with a CTE.
    """
    customers_data = [
        (1, "Alice", "West"),
        (2, "Bob", "West"),
        (3, "Carol", "East"),
        (4, "Dave", "East"),
        (5, "Eve", "West"),
    ]
    customers = spark.createDataFrame(customers_data, ["customer_id", "name", "region"])

    orders_data = [
        (101, 1, "2024-01-05", 200, "COMPLETED"),
        (102, 1, "2024-02-10", 150, "COMPLETED"),
        (103, 2, "2024-01-20", 500, "COMPLETED"),
        (104, 2, "2024-03-01", 100, "CANCELLED"),
        (105, 3, "2024-01-15", 300, "COMPLETED"),
        (106, 4, "2024-02-01", 700, "COMPLETED"),
        (107, 4, "2024-02-20", 50, "COMPLETED"),
        (108, 5, "2024-01-10", 400, "COMPLETED"),
        (109, 5, "2024-03-15", 600, "COMPLETED"),
    ]
    orders = spark.createDataFrame(
        orders_data, ["order_id", "customer_id", "order_date", "amount", "status"]
    )
    from pyspark.sql.window import Window
    # TODO: implement here
    df_final = customers.join(orders.filter(col('status')=='COMPLETED'), on = (customers['customer_id']==orders['customer_id']), how = 'left')\
        .select(col('region'),customers['customer_id'],col('name').alias('customer_name'),col('order_id'),col('order_date'),col('amount'))\
        .groupBy('region','customer_id','customer_name')\
        .agg(sum('amount').alias('total_spend'))\
        .withColumns({'region_rank':rank().over(Window.partitionBy('region').orderBy(col('total_spend').desc()))})\
        .filter(col('region_rank') <= 2)
    result = df_final

    return result


def exercise_10():
    """
    Problem 10: union() vs unionByName(), and the UNION ALL-not-UNION gotcha

    You're given two DataFrames of sales batches. Note `batch2`'s columns are
    in a DIFFERENT ORDER than `batch1`'s, on purpose:
        batch1 (columns: region, product, amount)
        region | product | amount
        -------|---------|-------
        West   | Widget  | 100
        West   | Gadget  | 200

        batch2 (columns: product, region, amount -- same names, different order!)
        product | region | amount
        --------|--------|-------
        Gizmo   | East   | 150
        Gadget  | East   | 250

    Tasks:
      1. `naive_union`: combine batch1 and batch2 with plain `.union()`.
         Notice the result is WRONG on purpose -- this is the point of the
         exercise. Look at the region/product values and see how they got
         scrambled.
      2. `correct_union`: combine them with `.unionByName()` instead, and see
         how it fixes the scrambling.
      3. `deduped`: union `batch1` with itself, notice every row appears
         TWICE (not deduplicated), then apply `.distinct()` to get back to
         the original 2 unique rows.

    Expected output:
      Task 1 (naive_union) -- WRONG on purpose, columns keep batch1's names
      but batch2's values land in the wrong slots:
        West,   Widget, 100
        West,   Gadget, 200
        Gizmo,  East,   150   <- region='Gizmo' (a product name!), product='East' (a region!)
        Gadget, East,   250   <- same problem
      Task 2 (correct_union) -- values correctly aligned by column name:
        West, Widget, 100
        West, Gadget, 200
        East, Gizmo,  150
        East, Gadget, 250
      Task 3 (deduped): back to exactly batch1's 2 original rows.

    Useful DataFrame methods / built-in functions:
        - df1.union(df2)
              combines rows from two DataFrames of the same column COUNT,
              matching columns by POSITION, not by name. If column order
              differs between the two DataFrames (as it deliberately does
              here), this silently produces wrong data -- no error, just
              misaligned values landing under the wrong column names.
                  batch1.union(batch2)   # dangerous here -- batch2's columns aren't in batch1's order

        - df1.unionByName(df2, allowMissingColumns=False)
              combines rows matching columns by NAME instead of position --
              safe regardless of column order.
                  batch1.unionByName(batch2)
              allowMissingColumns=True (Spark 3.1+) fills in NULL for any
              column present on one side but missing on the other, instead of
              raising an error:
                  batch1.unionByName(batch2, allowMissingColumns=True)

        - df1.union(df2).distinct()
              .union() does NOT deduplicate on its own -- despite SQL's plain
              `UNION` (no ALL) implying deduplication, PySpark's .union()
              actually behaves like SQL's `UNION ALL` (every row kept,
              duplicates included). Chain .distinct() explicitly for SQL
              UNION-style behavior.
                  combined = batch1.union(batch1)   # 4 rows -- every row duplicated
                  deduped = combined.distinct()      # back to 2 unique rows
    """
    batch1_data = [
        ("West", "Widget", 100),
        ("West", "Gadget", 200),
    ]
    batch1 = spark.createDataFrame(batch1_data, ["region", "product", "amount"])

    batch2_data = [
        ("Gizmo", "East", 150),
        ("Gadget", "East", 250),
    ]
    batch2 = spark.createDataFrame(batch2_data, ["product", "Region", "amount"])
    # Capitalization (case-sensitivity) in column names does not seem to matter so region == Region
    # TODO: implement here
    df_final = batch1.unionByName(batch2)
    result = df_final

    return result


def exercise_11():
    """
    Problem 11: string / number / date manipulation toolkit
    (you already know the SQL versions of these -- this is purely a naming
    translation exercise, no new concepts)

    You're given a `product_catalog` DataFrame:
        product_id | product_name         | price  | stock | last_restock
        -----------|----------------------|--------|-------|-------------
        1          |   wireless mouse     | 29.999 | 15    | 2024-01-10
        2          | USB-C Cable          | 9.5    | NULL  | 2024-02-15
        3          | mechanical KEYBOARD  | 89.994 | 3     | NULL

    Tasks:
      1. `clean_name`: trim whitespace and title-case `product_name`.
      2. `price_rounded` / `price_with_tax`: round `price` to 2 decimals, and
         separately compute `price * 1.08` (8% tax) also rounded to 2 decimals.
      3. `stock_filled`: replace NULL `stock` with 0.
      4. `restock_year` / `restock_month`: extract the year and month from
         `last_restock` (NULL last_restock -> NULL year/month, that's fine).
      5. `display_label`: a single string combining clean_name and
         price_rounded, e.g. "Wireless Mouse - 30.0" (separator: " - ").

    Expected output (approximate -- exact decimal-to-string formatting can
    vary slightly by Spark version, judge by concept not exact digits):
        1  clean_name='Wireless Mouse'      price_rounded=30.0  price_with_tax=32.4   stock_filled=15  restock_year=2024  restock_month=1  display_label='Wireless Mouse - 30.0'
        2  clean_name='Usb-c Cable'         price_rounded=9.5   price_with_tax=10.26  stock_filled=0   restock_year=2024  restock_month=2  display_label='Usb-c Cable - 9.5'
        3  clean_name='Mechanical Keyboard' price_rounded=89.99 price_with_tax=97.19  stock_filled=3   restock_year=NULL  restock_month=NULL  display_label='Mechanical Keyboard - 89.99'
    Note row 2's clean_name: initcap() only splits words on WHITESPACE (not
    on '-'), and lowercases the rest of each word -- "USB-C" becomes
    "Usb-c", not "USB-C". A real gotcha, not a typo -- worth knowing before
    it surprises you mid-interview.

    Useful DataFrame methods / built-in functions:
        - trim(col) / ltrim(col) / rtrim(col)
              strip whitespace -- trim does both sides, ltrim/rtrim do one side only.
                  trim(col("product_name"))

        - initcap(col)
              title-cases a string -- BUT splits words on whitespace only and
              lowercases everything else, per the gotcha above.
                  initcap(trim(col("product_name")))

        - round(col, scale) / ceil(col) / floor(col)
              numeric rounding. round() takes a second arg for decimal places
              (default 0); ceil/floor always round to the nearest integer.
                  round(col("price"), 2)
                  round(col("price") * 1.08, 2)

        - coalesce(*cols)
              returns the first non-NULL value across multiple columns/exprs,
              left to right -- the standard NULL-filling idiom, same as SQL.
                  coalesce(col("stock"), lit(0))
              multi-column fallback chain (not just a single default):
                  coalesce(col("stock"), col("backup_stock"), lit(0))

        - year(col) / month(col) / dayofmonth(col) / dayofweek(col) / quarter(col)
              extract a date part as an integer. All take a date/timestamp
              column directly.
                  year(col("last_restock"))
                  month(col("last_restock"))

        - concat_ws(sep, *cols)
              joins multiple columns into one string with a separator,
              skipping NULLs automatically (plain concat() does NOT skip
              NULLs -- one NULL input makes the whole result NULL, which is
              rarely what you want -- prefer concat_ws even for a single
              separator).
                  concat_ws(" - ", col("clean_name"), col("price_rounded").cast("string"))

        - col.cast(dataType)
              type conversion -- needed above since concat_ws expects string
              arguments, not a DoubleType.
                  col("price_rounded").cast("string")
                  col("price_rounded").cast("int")

        - a few more worth recognizing by name even without a dedicated task
          here (same idea as the rest -- you already know these from SQL):
              date_add(col, days) / date_sub(col, days)   -- add/subtract N days
              months_between(end, start)                  -- fractional months between two dates
              greatest(*cols) / least(*cols)               -- row-wise max/min across columns
              lpad(col, len, pad) / rpad(col, len, pad)    -- fixed-width zero/char padding
              current_date() / current_timestamp()         -- today's date / now, as literals
    """
    data = [
        (1, "  wireless mouse", 29.999, 15, "2024-01-10"),
        (2, "USB-C Cable", 9.5, None, "2024-02-15"),
        (3, "mechanical KEYBOARD", 89.994, 3, None),
    ]
    df = spark.createDataFrame(data, ["product_id", "product_name", "price", "stock", "last_restock"])

    # TODO: implement here
    result = df

    return result


def exercise_12():
    """
    Problem 12: consecutive active days per user ("gaps and islands")

    This is a well-known, commonly recognized SQL/data interview pattern --
    worth calling it "gaps and islands" out loud if it comes up, that name
    signals you've seen it before.

    You're given an `sf_events` DataFrame -- one row per (user, day) they were
    active:
        user_id | record_date
        --------|------------
        1       | 2024-01-01
        1       | 2024-01-02
        1       | 2024-01-03
        1       | 2024-01-05
        2       | 2024-01-01
        2       | 2024-01-03
        2       | 2024-01-04
        2       | 2024-01-05
        3       | 2024-01-01

    Task: find every run of CONSECUTIVE active days per user (2+ days in a
    row), with the streak's start date, end date, and length.

    The technique (the actual "gaps and islands" trick):
      1. `rn`: row_number() per user, ordered by record_date.
      2. `grp`: record_date MINUS rn (in days). Within an unbroken run of
         consecutive dates, both record_date and rn increase by exactly 1
         per row -- so this subtraction is CONSTANT for the whole run, and
         changes the moment there's a gap. This constant becomes a natural
         grouping key for each "island" of consecutive dates.
      3. Group by (user_id, grp): streak_start = min(record_date),
         streak_end = max(record_date), streak_length = count(*).
      4. Filter to streak_length >= 2 -- single isolated days aren't a
         "consecutive streak."

    Expected output (user_id, streak_start, streak_end, streak_length):
        1  2024-01-01  2024-01-03  3
        2  2024-01-03  2024-01-05  3
    (User 1's 2024-01-05 is isolated -- length 1, filtered out. User 2's
    2024-01-01 is isolated -- length 1, filtered out. User 3 has no streak
    at all -- a single row, filtered out entirely.)

    Useful DataFrame methods / built-in functions:
        - row_number().over(windowSpec)
              same pattern as exercise 4 -- sequential numbering per user,
              ordered by date.
                  from pyspark.sql.window import Window
                  w = Window.partitionBy("user_id").orderBy("record_date")
                  df.withColumn("rn", row_number().over(w))

        - date_sub(col, days)
              subtracts a number of days from a date column. `days` can be
              an int OR another Column (like `rn` here) -- this is the core
              of the trick.
                  df.withColumn("grp", date_sub(col("record_date"), col("rn")))

        - groupBy(...).agg(min(...), max(...), count(...))
              same aggregation pattern as exercise 2, just with min/max
              added alongside count -- all standard aggregate functions.
                  df.groupBy("user_id", "grp").agg(
                      min("record_date").alias("streak_start"),
                      max("record_date").alias("streak_end"),
                      count("record_date").alias("streak_length"),
                  )

        - df.filter(col("streak_length") >= 2)
              same post-aggregation filtering pattern as exercise 2's HAVING
              equivalent -- applied after the groupBy/agg, not before.
    """
    data = [
        (1, "2024-01-01"),
        (1, "2024-01-02"),
        (1, "2024-01-03"),
        (1, "2024-01-05"),
        (1, "2024-01-06"),
        (1, "2024-01-09"),
        (2, "2024-01-01"),
        (2, "2024-01-03"),
        (2, "2024-01-04"),
        (2, "2024-01-05"),
        (3, "2024-01-01"),
    ]
    df = spark.createDataFrame(data, ["user_id", "record_date"])
    df = df.withColumn("record_date", to_date(col("record_date")))
    
    from pyspark.sql.window import Window
    # TODO: implement here
    df_ordered = df.select('user_id','record_date').orderBy('user_id','record_date')\
        .withColumns({'test':concat_ws('-',(col('user_id')),col('record_date'))
        ,'rank':row_number().over(Window.partitionBy('user_id').orderBy('record_date'))
        ,'island':date_add(col('record_date'),-1*(col('rank')-1))
        })
    df_final = df_ordered.withColumns({
        'streak_start_date':min('record_date').over(Window.partitionBy('user_id','island'))
        })
    result = df_final

    return result


def exercise_13():
    """
    Problem 13: sessionization (time-gap-based session grouping)

    The natural harder version of exercise 12's gaps-and-islands trick --
    same underlying idea (a running flag that separates "islands"), but the
    boundary is now a TIME GAP THRESHOLD instead of a fixed 1-day step. This
    is one of the most commonly asked window-function interview problems.

    You're given a `user_events` DataFrame:
        user_id | event_time
        --------|--------------------
        1       | 2024-01-01 10:00:00
        1       | 2024-01-01 10:10:00
        1       | 2024-01-01 10:25:00
        1       | 2024-01-01 11:10:00
        1       | 2024-01-01 11:15:00
        2       | 2024-01-01 09:00:00
        2       | 2024-01-01 09:50:00
        2       | 2024-01-01 10:00:00

    Task: assign each event a `session_id` per user, where a NEW session
    starts whenever the gap since that user's previous event exceeds 30
    minutes (a user's very first event always starts session 1). Then
    summarize each session's start time, end time, and event count.

    The technique:
      1. `prev_event_time`: lag(event_time) per user, ordered by event_time
         (same lag() pattern as exercise 4).
      2. `gap_minutes`: minutes between event_time and prev_event_time --
         convert both to epoch seconds first (unix_timestamp), subtract,
         divide by 60. (First event per user: prev_event_time is NULL, so
         gap_minutes is NULL too -- treat that as "start a new session".)
      3. `new_session_flag`: 1 if gap_minutes > 30 OR prev_event_time IS
         NULL, else 0 (when/otherwise, same pattern as exercise 1).
      4. `session_id`: cumulative SUM of new_session_flag per user, ordered
         by event_time (rowsBetween unboundedPreceding, currentRow) -- this
         is EXACTLY exercise 4's running_total technique, just applied to a
         0/1 flag instead of a dollar amount. Each time a new session
         starts, the running sum ticks up by 1, giving every event its
         session number for free.
      5. groupBy(user_id, session_id): session_start = min(event_time),
         session_end = max(event_time), event_count = count(*).

    Expected output (user_id, session_id, session_start, session_end, event_count):
        1  1  10:00:00  10:25:00  3
        1  2  11:10:00  11:15:00  2
        2  1  09:00:00  09:00:00  1
        2  2  09:50:00  10:00:00  2
    (User 1: gap 10:25->11:10 is 45 min > 30, new session. User 2: gap
    09:00->09:50 is 50 min > 30, new session; 09:50->10:00 is 10 min, same
    session.)

    Useful DataFrame methods / built-in functions:
        - unix_timestamp(col)
              converts a timestamp column to epoch seconds (a plain long) --
              the simplest way to get a numeric difference between two
              timestamps in a specific unit like minutes.
                  (unix_timestamp(col("event_time")) - unix_timestamp(col("prev_event_time"))) / 60

        - lag(col).over(windowSpec)
              same as exercise 4 -- previous row's value within the
              partition, ordered by event_time.

        - when(condition, 1).otherwise(0)
              same conditional-flag pattern as exercise 1's amount_tier,
              just producing a 0/1 int instead of a string label.

        - sum(col).over(windowSpec.rowsBetween(Window.unboundedPreceding, Window.currentRow))
              the exact running-total technique from exercise 4, applied to
              a flag column -- a cumulative sum of "did a new session start
              here" IS the session number.

        - groupBy(...).agg(min(...), max(...), count(...))
              same summarization pattern as exercise 12's final step.
    """
    data = [
        (1, "2024-01-01 10:00:00"),
        (1, "2024-01-01 10:10:00"),
        (1, "2024-01-01 10:25:00"),
        (1, "2024-01-01 11:10:00"),
        (1, "2024-01-01 11:15:00"),
        (2, "2024-01-01 09:00:00"),
        (2, "2024-01-01 09:50:00"),
        (2, "2024-01-01 10:00:00"),
    ]
    df = spark.createDataFrame(data, ["user_id", "event_time"])
    df = df.withColumn("event_time", to_timestamp(col("event_time")))

    from pyspark.sql.window import Window
    # TODO: implement here
    df_flagged = df.orderBy('user_id','event_time').withColumns({'event_time_lag_1':lag('event_time').over(Window.partitionBy('user_id').orderBy('event_time'))
        ,'event_time_gap':timestamp_diff('minute','event_time_lag_1','event_time')
        ,'user_session_start_flag':when(col('event_time_gap').isNull(), col('event_time')).when(col('event_time_gap') > 30, col('event_time')).otherwise(None)
        
        })
    df_final = df_flagged.withColumns({
        'user_session_start_time':last('user_session_start_flag',ignorenulls=True).over(Window.partitionBy('user_id').orderBy('event_time').rowsBetween(Window.unboundedPreceding,Window.currentRow))
    })
    result = df_final

    # --- Reference solution (cumulative-sum-of-flag version, for comparison) ---
    # w_order = Window.partitionBy("user_id").orderBy("event_time")
    # df_ref = df.withColumn("prev_event_time", lag("event_time").over(w_order))
    # df_ref = df_ref.withColumn(
    #     "gap_minutes",
    #     (unix_timestamp(col("event_time")) - unix_timestamp(col("prev_event_time"))) / 60,
    # )
    # df_ref = df_ref.withColumn(
    #     "new_session_flag",
    #     when(col("prev_event_time").isNull(), 1).when(col("gap_minutes") > 30, 1).otherwise(0),
    # )
    # df_ref = df_ref.withColumn(
    #     "session_id",
    #     sum("new_session_flag").over(w_order.rowsBetween(Window.unboundedPreceding, Window.currentRow)),
    # )
    # result_ref = df_ref.groupBy("user_id", "session_id").agg(
    #     min("event_time").alias("session_start"),
    #     max("event_time").alias("session_end"),
    #     count("event_time").alias("event_count"),
    # )

    return result


def exercise_14():
    """
    Problem 14: overlapping intervals ("sweep line" / double-booking detection)

    Genuinely hard, less commonly asked than sessionization, but a strong
    signal question when it does come up. Also a nice tie-in to exercise
    10's union() -- building the "sweep line" event stream is itself a union.

    You're given a `bookings` DataFrame:
        room_id | booking_id | start_time | end_time
        --------|------------|------------|----------
        101     | b1         | 09:00      | 10:00
        101     | b2         | 09:30      | 10:30
        101     | b3         | 11:00      | 12:00
        102     | b4         | 09:00      | 10:00
        102     | b5         | 10:00      | 11:00

    Task: find which rooms have any DOUBLE-BOOKED (overlapping) time range.
    Room 101 has one (b1 and b2 overlap from 09:30-10:00). Room 102 does
    NOT -- b5 starts exactly when b4 ends, which is back-to-back, not
    overlapping.

    The technique ("sweep line"):
      1. Turn each booking into TWO events: a start event (time=start_time,
         delta=+1) and an end event (time=end_time, delta=-1). Build these
         as two separate DataFrames with the same schema and UNION them
         together (exercise 10's technique) into one `events` table.
      2. Order events by (room_id, time, delta) ascending. The tie-break on
         `delta` matters: at the exact same timestamp, end events
         (delta=-1) must sort BEFORE start events (delta=+1) -- since -1 <
         1, ordering by delta ascending achieves this automatically. This
         is what correctly treats "ends at 10:00, starts at 10:00" as
         non-overlapping instead of a false-positive conflict.
      3. `occupancy`: cumulative SUM of delta per room, ordered as above
         (rowsBetween unboundedPreceding, currentRow -- same running-total
         technique as exercises 4 and 13 again).
      4. Any room where `occupancy` ever exceeds 1 has an overlap --
         filter to occupancy > 1, then take the distinct room_ids.

    Expected output (room_ids with an overlap): just `101`.
    (Room 101's occupancy hits 2 at the 09:30 start event, since b1 hasn't
    ended yet. Room 102's occupancy never exceeds 1, because the tie-break
    processes b4's end event before b5's start event at 10:00.)

    Useful DataFrame methods / built-in functions:
        - building the events table (two DataFrames, same schema, unioned):
              starts = bookings.select(
                  col("room_id"), col("start_time").alias("time"), lit(1).alias("delta")
              )
              ends = bookings.select(
                  col("room_id"), col("end_time").alias("time"), lit(-1).alias("delta")
              )
              events = starts.union(ends)   # plain union() is fine here -- both sides already share column order

        - ordering with the tie-break:
              Window.partitionBy("room_id").orderBy("time", "delta")
              # delta ascending puts -1 (end) before +1 (start) at equal timestamps

        - sum(col).over(windowSpec.rowsBetween(Window.unboundedPreceding, Window.currentRow))
              same running-total technique as exercises 4 and 13, applied to
              the +1/-1 delta column -- this running sum IS the "how many
              bookings are active right now" occupancy count.

        - df.filter(col("occupancy") > 1).select("room_id").distinct()
              standard filter + distinct to get the final list of
              conflicted rooms, no new concepts.
    """
    bookings_data = [
        (101, "b1", "2024-01-01 09:00:00", "2024-01-01 10:00:00"),
        (101, "b2", "2024-01-01 09:30:00", "2024-01-01 10:30:00"),
        (101, "b3", "2024-01-01 11:00:00", "2024-01-01 12:00:00"),
        (102, "b4", "2024-01-01 09:00:00", "2024-01-01 10:00:00"),
        (102, "b5", "2024-01-01 10:00:00", "2024-01-01 11:00:00"),
    ]
    bookings = spark.createDataFrame(bookings_data, ["room_id", "booking_id", "start_time", "end_time"])
    bookings = bookings.withColumns({
        "start_time": to_timestamp(col("start_time")),
        "end_time": to_timestamp(col("end_time")),
    })

    # TODO: implement here
    
    start_events = bookings.select(col("room_id"), col("start_time").alias("time"), lit(1).alias("delta"))
    end_events = bookings.select(col("room_id"), col("end_time").alias("time"), lit(-1).alias("delta"))
    events = start_events.unionByName(end_events).orderBy(col("room_id"), col("time"))

    result = events                                                                   
    return result


def exercise_15():
    """
    Problem 15: cohort retention (join + date math + pivot)

    A classic "day/month N retention" analytics problem -- the kind of thing
    that shows up as a full take-home or a multi-part live-coding question.
    Introduces `.pivot()`, which nothing earlier in this set has used yet.

    You're given two DataFrames:
        users
        user_id | signup_date
        --------|------------
        1       | 2024-01-01
        2       | 2024-01-01
        3       | 2024-02-01

        activity
        user_id | activity_date
        --------|--------------
        1       | 2024-01-01
        1       | 2024-01-15
        1       | 2024-02-10
        2       | 2024-01-01
        2       | 2024-03-05
        3       | 2024-02-01
        3       | 2024-02-20

    Task: build a retention matrix -- one row per signup cohort (the month a
    user signed up), one column per "months since signup", with the count of
    DISTINCT active users in each cell.

    Steps:
      1. Join activity to users on user_id to get each activity row's
         signup_date alongside it.
      2. `cohort_month`: signup_date formatted as 'yyyy-MM' (date_format,
         same as exercise 5).
      3. `months_since_signup`: the integer number of calendar months
         between activity_date and signup_date. Prefer the year/month
         arithmetic version over months_between() for this -- see the note
         below on why.
      4. Group by (cohort_month, months_since_signup), counting DISTINCT
         user_id.
      5. Pivot `months_since_signup`'s values into columns, so each cohort
         is one row with one column per month-offset.

    Expected output (as a matrix, columns are months_since_signup values):
        cohort_month | 0 | 1    | 2
        -------------|---|------|-----
        2024-01      | 2 | 1    | 1
        2024-02      | 1 | NULL | NULL
    (Cohort 2024-01 has users 1 and 2; both active in month 0, only user 1
    active in month 1, only user 2 active in month 2. Cohort 2024-02 only
    has month-0 activity so far -- NULL, not 0, for months without data.)

    Useful DataFrame methods / built-in functions:
        - months_between(end, start)  vs.  (year(end)-year(start))*12 + (month(end)-month(start))
              months_between() returns a FRACTIONAL number of months based on
              day-of-month distance (e.g. slightly less than a whole month if
              the day-of-month hasn't been reached yet) -- fine for some use
              cases, but noisy for cohort bucketing where you want a clean
              integer "month 0 / month 1 / month 2" bucket regardless of
              which day of the month the activity happened on. The plain
              year/month arithmetic version gives a clean integer directly:
                  (year(col("activity_date")) - year(col("signup_date"))) * 12 \\
                      + (month(col("activity_date")) - month(col("signup_date")))

        - date_format(col, "yyyy-MM")
              same as exercise 5 -- used here to build the cohort label.

        - groupBy(...).agg(countDistinct(...))
              same aggregation pattern as exercise 2, with countDistinct
              instead of count -- matters here since the same user can have
              multiple activity rows in the same month-offset bucket.

        - df.groupBy(rowsCol).pivot(pivotCol).agg(aggExpr)
              NEW function. Sits between groupBy() and agg() in the chain:
              the DISTINCT VALUES of `pivotCol` become new output columns,
              and `aggExpr` (from the following .agg()) becomes the value
              populating each pivoted column, per group.
                  joined.groupBy("cohort_month").pivot("months_since_signup").agg(countDistinct("user_id"))
              optionally pass an explicit list of values as pivot()'s second
              arg -- this pins down exactly which columns appear (and their
              order), AND avoids an extra Spark job that would otherwise run
              first just to discover the distinct pivot values automatically:
                  .pivot("months_since_signup", [0, 1, 2])
    """
    users_data = [
        (1, "2024-01-01"),
        (2, "2024-01-01"),
        (3, "2024-02-01"),
    ]
    users = spark.createDataFrame(users_data, ["user_id", "signup_date"])
    users = users.withColumn("signup_date", to_date(col("signup_date")))

    activity_data = [
        (1, "2024-01-01"),
        (1, "2024-01-15"),
        (1, "2024-02-10"),
        (2, "2024-01-01"),
        (2, "2024-03-05"),
        (3, "2024-02-01"),
        (3, "2024-02-20"),
    ]
    activity = spark.createDataFrame(activity_data, ["user_id", "activity_date"])
    activity = activity.withColumn("activity_date", to_date(col("activity_date")))

    # TODO: implement here
    df = users.join(activity, on=(users["user_id"] == activity["user_id"]), how="left").select(users["signup_date"],users["user_id"],  activity["activity_date"]).withColumns({
        'cohort_month':date_format(col('signup_date'),'yyyy-MM')\
        ,'months_since_signup':months_between(col('activity_date'),col('signup_date')).cast('int')
    })
    df_final = df.groupBy('cohort_month').pivot('months_since_signup').agg(count_distinct('user_id'))
    result = df_final

    return result


if __name__ == "__main__":
    exercise_15().show()
