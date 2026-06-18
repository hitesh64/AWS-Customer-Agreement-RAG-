import sqlite3
from database import get_db_connection

def get_analytics_data() -> dict:
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(id) as total FROM query_logs")
    total_queries = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT question, COUNT(id) as frequency 
        FROM query_logs 
        GROUP BY question 
        ORDER BY frequency DESC 
        LIMIT 5
    """)
    most_frequent = [{"question": row["question"], "count": row["frequency"]} for row in cursor.fetchall()]

    cursor.execute("SELECT COUNT(id) as no_answer FROM query_logs WHERE answer_found = 0")
    no_answer_queries = cursor.fetchone()["no_answer"]

    cursor.execute("SELECT AVG(response_time) as avg_lat FROM query_logs")
    avg_latency_row = cursor.fetchone()["avg_lat"]
    average_latency = round(avg_latency_row, 4) if avg_latency_row else 0.0

    cursor.execute("""
        SELECT answer_found, COUNT(id) as count 
        FROM query_logs 
        GROUP BY answer_found
    """)
    found_vs_not = [{"status": "Found" if row["answer_found"] else "Not Found", "count": row["count"]} for row in cursor.fetchall()]

    conn.close()

    return {
        "total_queries": total_queries,
        "most_frequent_questions": most_frequent,
        "no_answer_queries": no_answer_queries,
        "average_latency": average_latency,
        "found_vs_not_found": found_vs_not
    }