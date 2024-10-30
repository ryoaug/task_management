from datetime import date
from app import app, db, User, Task


with app.app_context():
    # 既存のユーザー（例：user1）の取得
    user1 = User.query.filter_by(username='testuser1').first()
    user2 = User.query.filter_by(username='testuser2').first()


    task1 = Task(title='タスク1', due_date=date(2024,10,31), details='タスクの詳細1', category='仕事', is_completed=False, user_id=user1.id )
    task2 = Task(title='タスク2', due_date=date(2024,11,15), details='タスクの詳細2', category='趣味', is_completed=False, user_id=user2.id)
    task3 = Task(title='タスク3', due_date=date(2024,11,26), details='タスクの詳細3', category='仕事', is_completed=False, user_id=user1.id )
    task4 = Task(title='タスク4', due_date=date(2024,12,7), details='タスクの詳細4', category='趣味', is_completed=False, user_id=user2.id)
    task5 = Task(title='タスク5', due_date=date(2024,12,25), details='タスクの詳細5', category='仕事', is_completed=False, user_id=user1.id )
    task6 = Task(title='タスク6', due_date=date(2024,12,31), details='タスクの詳細6', category='趣味', is_completed=False, user_id=user2.id)

    # データを追加してコミット
    # db.session.add_all([user1, user2])  # 修正：リストで追加
    db.session.add_all([task1, task2,task3, task4, task5, task6])  # タスクを追加する場合は、こちらも修正
    db.session.commit()  # 変更をデータベースに保存

    print(task1.id)
    print(task2.id)