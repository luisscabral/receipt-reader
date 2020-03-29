import os

package_dir = os.path.abspath(os.path.dirname(__file__))
db_dir = os.path.join(package_dir, 'receipt.db')
# db = SQL("sqlite:///" + db_dir)
print(db_dir)