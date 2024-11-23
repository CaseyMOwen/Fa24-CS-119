import sys, time

import pyspark
from pyspark.conf import SparkConf
from pyspark.context import SparkContext
from pyspark.sql import SparkSession

from pyspark.sql.functions import window, avg,  col

def setLogLevel(sc, level):
    from pyspark.sql import SparkSession
    spark = SparkSession(sc)
    spark.sparkContext.setLogLevel(level)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: q3-stock-streaming.py <hostname> <port>", file=sys.stderr)
        sys.exit(-1)

    print ('Argv', sys.argv)
    
    host = sys.argv[1]
    port = int(sys.argv[2])
    print ('host', type(host), host, 'port', type(port), port)

    sc_bak = SparkContext.getOrCreate()
    sc_bak.stop()
    
    time.sleep(15)
    print ('Ready to work!')

    ctx = pyspark.SparkContext(appName = "Stock Streaming", master="local[*]")
    print ('Context', ctx)

    spark = SparkSession(ctx).builder.getOrCreate()
    sc = spark.sparkContext

    setLogLevel(sc, "WARN")

    print ('Session:', spark)
    print ('SparkContext', sc)
    

    # Create DataFrame representing the stream of input lines from connection to host:port
    lines = spark\
        .readStream\
        .format('socket')\
        .option('host', host)\
        .option('port', port)\
        .load()

    # Question 11
    aaplPrice = lines.selectExpr("split(value, '\t') as col").selectExpr("cast(col[0] as timestamp) as timestamp", "cast(col[1] as double) as AAPL").withWatermark("timestamp", "40 days")

    msftPrice = lines.selectExpr("split(value, '\t') as col").selectExpr("cast(col[0] as timestamp) as timestamp", "cast(col[2] as double) as MSFT").withWatermark("timestamp", "40 days")

    # Question 12
    # Also need 1 day prices so we can calculate the equiv number of MSFT shares to 1,000 shares of AAPL
    aapl1Day = aaplPrice\
        .groupBy(window(col("timestamp"), "1 day", "1 day"))\
        .agg(avg(col("AAPL")).alias("rolling_avg_appl_1"))\
        .selectExpr("window.end as window_end", "rolling_avg_appl_1")

    aapl10Day = aaplPrice\
        .groupBy(window(col("timestamp"), "10 days", "1 day"))\
        .agg(avg(col("AAPL")).alias("rolling_avg_appl_10"))\
        .selectExpr("window.end as window_end", "rolling_avg_appl_10")
    
    aapl40Day = aaplPrice\
        .groupBy(window(col("timestamp"), "40 days", "1 day"))\
        .agg(avg(col("AAPL")).alias("rolling_avg_appl_40"))\
        .selectExpr("window.end as window_end", "rolling_avg_appl_40")
    
    # Question 13
    msft1Day = msftPrice\
        .groupBy(window(col("timestamp"), "1 day", "1 day"))\
        .agg(avg(col("MSFT")).alias("rolling_avg_msft_1"))\
        .selectExpr("window.end as window_end", "rolling_avg_msft_1")

    msft10Day = msftPrice\
        .groupBy(window(col("timestamp"), "10 days", "1 day"))\
        .agg(avg(col("MSFT")).alias("rolling_avg_msft_10"))\
        .selectExpr("window.end as window_end", "rolling_avg_msft_10")
    
    msft40Day = msftPrice\
        .groupBy(window(col("timestamp"), "40 days", "1 day"))\
        .agg(avg(col("MSFT")).alias("rolling_avg_msft_40"))\
        .selectExpr("window.end as window_end", "rolling_avg_msft_40")

    # Question 14
    # Join on window_end since that is the "current day" to buy or sell on
    joined_streams = aapl1Day\
        .join(aapl10Day, "window_end")\
        .join(aapl40Day, "window_end")\
        .join(msft1Day, "window_end")\
        .join(msft10Day, "window_end")\
        .join(msft40Day, "window_end")\

    with open("trade_signals.txt", "w") as file:
        file.write("[")

    def print_to_file(text:str):
        filename = "trade_signals.txt"
        with open(filename, "a") as file:
            file.write(text + ",")
            
    previous_df = None
    def compare_and_print(batch_df, batch_id):
        '''
        Compare the rolling averages and print the result to file and console
        '''
        output_file = ""
        global previous_df
        current_df = batch_df.collect()
        if previous_df is not None:
            for current, previous in zip(current_df, previous_df):
                date = current["window_end"].date()
                print(date)
                print(f'aapl today: {current["rolling_avg_appl_1"]}')
                print(f'aapl 10-day: {current["rolling_avg_appl_10"]}')
                print(f'appl 40-day: {current["rolling_avg_appl_40"]}')

                print(f'msft today: {current["rolling_avg_msft_1"]}')
                print(f'msft 10-day: {current["rolling_avg_msft_10"]}')
                print(f'msft 40-day: {current["rolling_avg_msft_40"]}')
                
                previous_buy_appl = (previous["rolling_avg_appl_10"] > previous["rolling_avg_appl_40"])
                current_buy_appl = (current["rolling_avg_appl_10"] > current["rolling_avg_appl_40"])

                previous_buy_msft = (previous["rolling_avg_msft_10"] > previous["rolling_avg_msft_40"])
                current_buy_msft = (current["rolling_avg_msft_10"] > current["rolling_avg_msft_40"])

                if (previous_buy_appl and not current_buy_appl):
                    print(f'({date} sell 1000 shares AAPL)')
                    print_to_file(f'({date} sell 1000 shares AAPL)')
                elif (current_buy_appl and not previous_buy_appl):
                    print(f'({date} buy 1000 shares AAPL)')
                    print_to_file(f'({date} buy 1000 shares AAPL)')

                # Number of msft shares that are same dollar amount as 1,000 aapl shares
                msft_equiv_shares = 1000*current["rolling_avg_appl_1"]/current["rolling_avg_msft_1"]
                if (previous_buy_msft and not current_buy_msft):
                    print(f'({date} sell {msft_equiv_shares:.2f} shares MSFT)')
                    print_to_file(f'({date} sell {msft_equiv_shares:.2f} shares MSFT)')
                elif (current_buy_msft and not previous_buy_msft):
                    print(f'({date} buy {msft_equiv_shares:.2f} shares MSFT)')
                    print_to_file(f'({date} buy {msft_equiv_shares:.2f} shares MSFT)')

        previous_df = current_df

    query = joined_streams.writeStream\
        .foreachBatch(compare_and_print)\
        .start()

    query.awaitTermination()

    with open("trade_signals.txt", "a") as file:
        file.write("]")

