import sqlite3
import os

from src.utils.logger import logger


def list_all_thread_ids(db_path: str):
    """
    查询数据库中所有表里存在的唯一 thread_id
    """
    if not os.path.exists(db_path):
        logger.error(f"找不到数据库文件: {os.path.abspath(db_path)}")
        return []

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 使用 set 来去重，因为多个表可能包含相同的 thread_id
    unique_threads = set()

    try:
        # 1. 获取所有表名
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]

        # 2. 遍历表，寻找包含 thread_id 的表并提取 ID
        for table in tables:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [col[1] for col in cursor.fetchall()]

            if "thread_id" in columns:
                # 获取该表中所有不重复的 thread_id
                cursor.execute(f"SELECT DISTINCT thread_id FROM {table}")
                rows = cursor.fetchall()
                for row in rows:
                    if row[0]:  # 确保 ID 不为空
                        unique_threads.add(row[0])

        # 3. 打印结果
        if unique_threads:
            logger.info(f"数据库中共有 {len(unique_threads)} 个活动的会话 (thread_id):")
            for tid in sorted(list(unique_threads)):
                logger.info(f"  📍 {tid}")
        else:
            logger.info("数据库中尚未记录任何 thread_id。")

        return list(unique_threads)

    except Exception as e:
        logger.error(f"查询出错: {e}")
        return []
    finally:
        conn.close()


def final_safe_delete(db_path: str, thread_id: str):
    if not os.path.exists(db_path):
        logger.error(f"找不到数据库文件: {os.path.abspath(db_path)}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # 1. 获取数据库中真实存在的所有表名
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        existing_tables = [row[0] for row in cursor.fetchall()]

        # 2. 开启事务
        cursor.execute("BEGIN TRANSACTION;")

        found_any = False
        # 3. 动态检查每一张表
        for table in existing_tables:
            # 检查这张表里是否有 thread_id 这一列
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [col[1] for col in cursor.fetchall()]

            if "thread_id" in columns:
                # 只有表存在且包含 thread_id 列时才执行删除
                cursor.execute(f"DELETE FROM {table} WHERE thread_id = ?", (thread_id,))
                logger.info(f"已清理表: {table}")
                found_any = True

        conn.commit()
        if found_any:
            logger.info(f"成功：thread_id '{thread_id}' 的数据已彻底清除。")
        else:
            logger.info(f"数据库中未发现与 '{thread_id}' 相关的记录。")

    except Exception as e:
        conn.rollback()
        logger.error(f"运行出错: {e}")
    finally:
        conn.close()


# --- 调用执行 ---
# 请确保 DB_PATH 指向你项目根目录下的实际数据库文件名
# DB_PATH = "checkpoints.db"
# THREAD_TO_DELETE = "daily_study_1775126843"
# final_safe_delete(DB_PATH, THREAD_TO_DELETE)
# thread_ids = list_all_thread_ids(DB_PATH)
# for tid in thread_ids:
#     final_safe_delete(DB_PATH, tid)
