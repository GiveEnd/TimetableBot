import sqlite3 as sq
from create_bot import bot

def sql_start():
    global base, cur
    base = sq.connect('time_Table.db')
    cur = base.cursor()
    if base: 
        print('Data base connected OK!')
    base.execute('CREATE TABLE IF NOT EXISTS timeTable(id INTEGER PRIMARY KEY AUTOINCREMENT, date DATE, time TIME, name TEXT)')
    base.commit()

async def sql_add_command(state):
    async with state.proxy() as data:
        cur.execute('INSERT INTO timeTable VALUES (NULL , ?, ?, ?)', tuple(data.values()))
        base.commit()

async def sql_read2():
    return cur.execute('SELECT * FROM timeTable').fetchall()

async def sql_delete_command(data):
    cur.execute('DELETE FROM timeTable WHERE id == ?', (data,))
    base.commit()       

async def sql_date_out():
        items = cur.execute('SELECT DISTINCT date FROM timeTable').fetchall()
        list_items = [row[0] for row in items]
        return list_items
async def sql_list_name(index):
        items = cur.execute('SELECT id, time, name FROM timeTable WHERE date = ?', (index,)).fetchall()
        list_items = ['|' + str(row[0]) + '|' + row[1] + ' ' + row[2] for row in items]
        return list_items