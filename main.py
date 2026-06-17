import mysql.connector
import os
import hashlib
import secrets
from mysql.connector import Error
required = ["DB_HOST", "DB_USER", "DB_PASSWORD", "DB_NAME"]
for var in required:
    if not os.getenv(var):
        raise ValueError(f"Missing environment variable: {var}")
db=mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)
cursor=db.cursor()
current_user = None
user_acc = None
def login():
    global current_user
    global user_acc
    acc_no = input("Account : ")
    pin = input("PIN : ")
    query = """
    SELECT customer_id,acc_no,pin_hash,salt
    FROM account
    WHERE acc_no=%s
    """
    try:
        cursor.execute(query,(acc_no,))
    except Error as e:
        db.rollback()
        print("Database Error:",e)
    user = cursor.fetchone()
    if not user:
        return False
    if hash_pin(pin,user[3]) == user[2]:
        current_user = {
            "customer_id": user[0],
            "acc_no": user[1]
        }
        user_acc = current_user["acc_no"]
        return True
    return False
def verification():
    user_acc=input("Account : ")
    user_pin=int(input("Enter PIN : "))
    query="SELECT *FROM account WHERE acc_no=%s AND pin=%s"
    value=(user_acc,user_pin)
    try:
        cursor.execute(query,value)
    except Error as e:
        db.rollback()
        print("Database Error:",e)
    result=cursor.fetchone()
    return result,user_acc   
def hash_pin(pin, salt):
    return hashlib.sha256((pin + salt).encode()).hexdigest()
class bank:
    def create_new_acc(self):
        name=input("Enter your name : ")
        mobile=input("Enter your phone number : ")
        balance=int(input("Deposit Some Amount (Minimum balance = Rs. 500) : "))
        if balance < 500:
            print("Minimum opening balance is 500")
            return
        pin=input("Set a 4-digit pin : ")
        if len(pin)==4 and pin.isdigit():
            salt = secrets.token_hex(16)
            pin_hash = hash_pin(pin, salt)
            query = """
            INSERT INTO account
            (name,mobile,balance,pin_hash,salt)
            VALUES(%s,%s,%s,%s,%s)
            """
            values = (
                name,
                mobile,
                balance,
                pin_hash,
                salt
            )
            try:
                cursor.execute(query,values)
                db.commit()
                customer_id = cursor.lastrowid
                acc = f"ACC{100000 + customer_id}"
                query = """
                UPDATE account
                SET acc_no=%s
                WHERE customer_id=%s
                """
                cursor.execute(query,(acc,customer_id))
                db.commit()
            except Error as e:
                db.rollback()
                print("Database Error:",e)
            print("---------------------------------------")
            print("      ACCOUNT CREATED SUCCESSFULLY")
            print("---------------------------------------")
            print(f"Holder name : {name}\nAccount Number : {acc}\nBalance : {balance}")
            print("---------------------------------------")
        else:
            print("----------------------------------")
            print(" Invalid input! Pin must be 4-digit")
            print("----------------------------------")
    def change_pin(self):
        result,user_acc=verification()
        if result:
            new_pin=input("Enter new pin : ")
            if len(new_pin) == 4 and new_pin.isdigit():
                salt = secrets.token_hex(16)
                pin_hash = hash_pin(new_pin,salt)
                query = """
                UPDATE account
                SET pin_hash=%s,
                    salt=%s
                WHERE acc_no=%s
                """
                values=(pin_hash,salt,user_acc)
                try:
                    cursor.execute(query,values)
                    db.commit()
                except Error as e:
                    db.rollback()
                    print("Database Error:",e)
                print("------------------------------")
                print("Pin Changed Successfully")
                print("------------------------------")
        else:
            print("---------------------------")
            print("Account Not Found")
            print("Invalid Account or Pin!")
            print("----------------------------")
    def credit_balance(self):
        result,user_acc=verification()
        if result:
            new_amount = int(input("Amount : "))
            if new_amount <= 0:
                print("Amount must be greater than zero")
                return
            query="UPDATE account SET balance=balance+%s WHERE acc_no=%s"
            values=(new_amount,user_acc)
            try:
                cursor.execute(query,values)
                db.commit()
            except Error as e:
                db.rollback()
                print("Database Error:",e)
            query="SELECT balance FROM account WHERE acc_no=%s"
            values=(user_acc,)
            try:
                cursor.execute(query,values)
            except Error as e:
                db.rollback()
                print("Database Error:",e)
            result_data=cursor.fetchone()
            print("-----------------------------------")
            print("Amount Deposited Successfully")
            print(f"Current Balance : ",result_data[0])
            print("-----------------------------------")
        else:
            print("---------------------------")
            print("Account Not Found")
            print("Invalid Account or Pin!")
            print("----------------------------")
    def debit_amount(self):
        result,user_acc=verification()
        if result:
            user_amount=int(input("Enter Amount : "))
            if user_amount <= 0:
                print("Amount must be greater than zero")
                return
            query="SELECT balance FROM account WHERE acc_no=%s"
            try:
                cursor.execute(query,(user_acc,))
            except Error as e:
                db.rollback()
                print("Database Error:",e)
            data=cursor.fetchone()
            remaining_balance = data[0] - user_amount
            if user_amount>data[0]:
                print("---------------------------")
                print("Insufficient balance")
                print("Balance : ",data[0])
                print("---------------------------")
                return
            elif remaining_balance < 500:
                print("---------------------------")
                print("Account Must Have Minimum Balance = Rs. 500") 
                print("Current Balance : ",data[0])
                print("---------------------------")
            else:
                query="UPDATE account SET balance=balance-%s WHERE acc_no=%s"
                values=(user_amount,user_acc)
                try:
                    cursor.execute(query,values)
                    db.commit()
                except Error as e:
                    db.rollback()
                    print("Database Error:",e)
                query="SELECT balance FROM account WHERE acc_no=%s"
                try:
                    cursor.execute(query,(user_acc,))
                except Error as e:
                    db.rollback()
                    print("Database Error:",e)
                data=cursor.fetchone()
                print("-------------------------------")
                print("Amount Withdrawal Completed Successfully")
                print("Current Balance : ",data[0])
                print("-------------------------------")
        else:
            print("---------------------------")
            print("Account Not Found")
            print("Invalid Account or Pin!")
            print("----------------------------")
    def delete_acc(self):
        result,acc=verification()
        if result:
            if result[3]!=0:
                print("ACCOUNT HAS SOME BALANCE")
                return
            else:
                print("Are you sure you want to delete your account permanently? (y/n) : ")
                user_response=input()
                if user_response=='y' or user_response=='Y':
                    query="DELETE FROM account WHERE acc_no=%s"
                    try:
                        cursor.execute(query,(acc,))
                        db.commit()
                    except Error as e:
                        db.rollback()
                        print("Database Error:",e)
                    print("---------------------------------")
                    print("Account Deleted Successfully ")
                    print("---------------------------------")
                else:
                    return  
        else:
            print("---------------------------")
            print("Account Not Found")
            print("Invalid Account or Pin!")
            print("----------------------------")   
    def show_all(self):
        query="SELECT acc_no,name FROM account"
        try:
            cursor.execute(query)
        except Error as e:
            db.rollback()
            print("Database Error:",e)
        result=cursor.fetchall()
        if result:
            print("========= All Accounts =============")
            print("ACCOUNT NO.             NAME")
            print("-----------------------------------")
            i=1
            for row in result:
                print(f"{i}.{row[0]}\t\t{row[1]}")
                i+=1
        else:
            print("----------------------")
            print("No Accounts")
            print("----------------------")
    def forgot(self):
        user_acc=input("Account No.:")
        mobile=input("Enter Registered Phone No.:")
        query="SELECT * FROM account WHERE acc_no=%s AND mobile=%s"
        values=(user_acc,mobile)
        try:
            cursor.execute(query,values)
        except Error as e:
            db.rollback()
            print("Database Error:",e)
        result=cursor.fetchone()
        if result:
            new_pin=input("Enter New Pin : ")
            if len(new_pin) == 4 and new_pin.isdigit():
                salt = secrets.token_hex(16)
                pin_hash = hash_pin(new_pin,salt)
                query = """
                UPDATE account
                SET pin_hash=%s,
                    salt=%s
                WHERE acc_no=%s
                """
                values=(pin_hash,salt,user_acc)
                try: 
                    cursor.execute(query,values)
                    db.commit()
                except Error as e:
                    db.rollback()
                    print("Database Error:",e)
                print("------------------------------")
                print("Pin Changed Successfully")
                print("-------------------------------")
        else:
            print("----------------------------")
            print("Invalid Account or Mobile!")
            print("----------------------------")
    def acc_info(self):
        result,user_acc=verification()
        if result:
            query="SELECT name,mobile,balance FROM account WHERE acc_no=%s"
            try:
                cursor.execute(query,(user_acc,))
            except Error as e:
                db.rollback()
                print("Database Error:",e)
            res=cursor.fetchall()
            print("=========== ACCOUNT INFO ============")
            for row in res:
                print("ACCOUNT NUMBER : ",user_acc)
                print("HOLDER NAME    : ",row[0])
                print("PHONE NUMBER   : ",row[1])
                print("BALANCE        : ",row[2])
                break
        else:
            print("---------------------")
            print("  ACCOUNT NOT FOUND  ")
            print("----------------------")
b=bank()
while True:
    print("====================================")
    print("       BANK MANAGEMENT SYSTEM    ")
    print("====================================")
    print("1.CREATE ACCOUNT\n2.ACCOUNT INFO\n3.DEPOSIT\n4.WITHDRAWAL\n5.CHANGE PIN\n6.FORGOT PIN \n7.DELETE ACCOUNT\n8.EXIT")
    try:
        ch=int(input("Enter your choice : "))
        if ch==1:
            b.create_new_acc()
        elif ch==2:
            b.acc_info()
        elif ch==3:
            b.credit_balance()
        elif ch==4:
            b.debit_amount()
        elif ch==5:
            b.change_pin()
        elif ch==6:
            b.forgot()
        elif ch==7:
            b.delete_acc()
        elif ch==8:
            try:
                db.commit()
            except Error as e:
                db.rollback()
                print("Database Error:",e)
            db.close()
            print("Exiting...\n")
            break
        else:
            print("Invalid choice! Try Again")
    except ValueError:
        print("=====================================")
        print("Invalid Input!")
        print("=====================================")
