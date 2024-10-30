from app import db, User

db.create_all()  # テーブルを作成

user1 = User(username='testuser1', password='111')
user2 = User(username='testuser2', password='222')

# タスクを追加する場合は、以下のコードをコメント解除
# task1 = Task(title='タスク1', due_date='2024-10-31', details='タスクの詳細1', category='仕事', is_completed=False, user=user1)
# task2 = Task(title='タスク2', due_date='2024-11-15', details='タスクの詳細2', category='趣味', is_completed=False, user=user1)

# データを追加してコミット
db.session.add_all([user1, user2])  # 修正：リストで追加
# db.session.add_all([task1, task2])  # タスクを追加する場合は、こちらも修正
db.session.commit()  # 変更をデータベースに保存

print(user1.id)
print(user2.id)
