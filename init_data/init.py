import glob
import os
import logging
import uuid

from calendar import month_abbr
from tqdm import tqdm

import pandas as pd
import numpy as np

from datetime import datetime
from passlib.context import CryptContext
from database.utils import get_session
from database.models import User, Board, Post, create_table

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
MONTH_ABBR = { month_abbr[month]:month for month in range(1, 13) }

def get_password_hash(password):
    return pwd_context.hash(password)

def get_current_users(db):
    users = db.query(User).all()
    user_dict = {user.username:user.user_id for user in users}
    return user_dict

def create_initial_users(db, user_dict):
    
    init_users = ['aics_admin1', 'aics_admin2']
    for init_user in init_users:
        if init_user in user_dict: continue

        new_user_id = uuid.uuid4()
        user_dict[init_user] = new_user_id

        new_user = User(
            user_id = new_user_id,
            username = init_user, 
            password = get_password_hash(init_user),
            email = f'{init_user}@asus.com',
            company = 'ASUS',
            place = 'Taipei',
            phone = '0987-654321',
        )
        db.add(new_user)
    db.commit()
    return

def create_users(users, db, user_dict):
    cnt, pwd = 0, get_password_hash('0000')

    for username in users:
        if username in user_dict: continue

        new_user_id = uuid.uuid4()
        user_dict[username] = new_user_id

        new_user = User(
            user_id = new_user_id,
            username = username, 
            password = pwd,
            email = f'{username}@asus.com',
            company = 'ASUS',
            place = 'Taipei',
            phone = '0987-654321',
        )
        db.add(new_user)
        cnt += 1
    db.commit()
    return cnt

def create_board(board_name, db):
    board = db.query(Board).filter(Board.board_name==board_name).first()
    if board: return False

    new_board = Board(
        board_id = uuid.uuid4(),
        board_name = board_name
    )
    db.add(new_board)
    db.commit()

    return True

def create_posts(board_name, posts, db, user_dict):

    board_id = db.query(Board).filter(Board.board_name==board_name).first().board_id
    
    s_cnt = 0
    trange = tqdm(posts.iterrows(), total=len(posts), desc='create posts')
    for _, row in trange:

        # datetime
        try:
            _, month, day, time, year = row['post_time'].split()
        
            hour, minute, second = map(int, time.split(':'))
            date = datetime(int(year), MONTH_ABBR[month], int(day), hour, minute, second)

            new_post = Post(
                post_id = uuid.uuid4(),
                title = row['title'],
                content = row['article'],
                author_id = user_dict[row['author']],
                like = row['like'],
                hate = row['hate'],
                post_time = date,
                board_id = board_id
            )
            db.add(new_post)
            s_cnt += 1
        except:
            continue

    db.commit()

    return s_cnt, len(posts)-s_cnt
    


db = get_session()
def main():
    create_table()
    boards = glob.glob('./database/ptt_data/*.csv')

    user_dict = get_current_users(db)
    create_initial_users(db, user_dict)

    for board in boards:
        
        with open(board, 'r') as f: posts = pd.read_csv(f)

        users = np.unique(posts['author'])
        
        root, _ = os.path.splitext(board)
        board_name = root.split('/')[-1]

        logging.info('Create new users')
        count = create_users(users, db, user_dict)
        logging.info(f'Successfully create {count} users')

        logging.info(f'Creating board {board_name}')
        board_state = create_board(board_name, db)
        logging.info(f'{board_state} creates board {board_name}')

        if board_state:
            logging.info(f'Creating posts in board {board_name}')
            s_cnt, f_cnt = create_posts(board_name, posts, db, user_dict)
            logging.info(f'{board_name} successfully creates {s_cnt} posts, fails {f_cnt} posts')

    db.close()

if __name__ == '__main__':

    logging.basicConfig(format='%(asctime)s | %(levelname)s | %(message)s',
                        level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')

    main()
