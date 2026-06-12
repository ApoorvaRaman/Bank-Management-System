import mysql.connector
import random
db=mysql.connector.connect(
    host="localhost",
    user="username",
    password="password",
    database="DB_name"
)
cursor=db.cursor()
def acc_generate():
    password=random.randint(1,99)
    return "ACC28"+str(password)
def verification():
    user_acc=input("Account : ")
    user_pin=int(input("Enter PIN : "))
    query="SELECT *FROM account WHERE acc_no=%s AND pin=%s"
    value=(user_acc,user_pin)
    cursor.execute(query,value)
    result=cursor.fetchone()
    return result,user_acc   
class bank:
    def create_new_acc(self):
        acc=acc_generate()
        name=input("Enter your name : ")
        mobile=int(input("Enter your phone number : "))
        balance=int(input("Deposit Some amount min(100) : "))
        pin=input("Set a 4-digit Pin : ")
        if len(pin)==4 and pin.isdigit():
            query="INSERT INTO account(acc_no,name,mobile,balance,pin) VALUES(%s,%s,%s,%s,%s)"
            values=(acc,name,mobile,balance,pin)
            cursor.execute(query,values)
            db.commit()
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
            new_pin=int(input("Enter new pin : "))
            query="UPDATE account SET pin=%s WHERE acc_no=%s"
            values=(new_pin,user_acc)
            cursor.execute(query,values)
            db.commit()
            print("------------------------------")
            print("     Pin Changed Successfully  ")
            print("------------------------------")
        else:
            print("---------------------------")
            print("Account Not Found")
            print("Invalid Account or Pin!")
            print("----------------------------")
    def credit_balance(self):
        result,user_acc=verification()
        if result:
            new_amount=int(input("Amount : "))
            query="UPDATE account SET balance=balance+%s WHERE acc_no=%s"
            values=(new_amount,user_acc)
            cursor.execute(query,values)
            db.commit()
            query="SELECT balance FROM account WHERE acc_no=%s"
            values=(user_acc,)
            cursor.execute(query,values)
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
            query="SELECT balance FROM account WHERE acc_no=%s"
            cursor.execute(query,(user_acc,))
            data=cursor.fetchone()
            if user_amount>data[0]:
                print("---------------------------")
                print("     Insufficient balance  ")
                print("Balance : ",data[0])
                print("---------------------------")
                return
            else:
                query="UPDATE account SET balance=balance-%s WHERE acc_no=%s"
                values=(user_amount,user_acc)
                cursor.execute(query,values)
                db.commit()
                query="SELECT balance FROM account WHERE acc_no=%s"
                cursor.execute(query,(user_acc,))
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
                    cursor.execute(query,(acc,))
                    db.commit()
                    print("---------------------------------")
                    print("  Account Deleted Successfully ")
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
        cursor.execute(query)
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
            print("      No Accounts    ")
            print("----------------------")
    def forgot(self):
        user_acc=input("Account No.:")
        mobile=int(input("Enter Registered Phone No.:"))
        query="SELECT * FROM account WHERE acc_no=%s AND mobile=%s"
        values=(user_acc,mobile)
        cursor.execute(query,values)
        result=cursor.fetchone()
        if result:
            new_pin=int(input("Enter New Pin : "))
            query="UPDATE account SET pin=%s WHERE acc_no=%s"
            values=(new_pin,user_acc)
            cursor.execute(query,values)
            db.commit()
            print("------------------------------")
            print("   PIN CHANGED SUCCESSFULLY")
            print("-------------------------------")
        else:
            print("---------------------------")
            print("Invalid Account or Mobile!")
            print("----------------------------")
    def acc_info(self):
        result,user_acc=verification()
        if result:
            query="SELECT name,mobile,balance FROM account WHERE acc_no=%s"
            cursor.execute(query,(user_acc,))
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
            db.close()
            print("EXITING...\n")
            break
        else:
            print("Invalid choice! Try Again")
    except ValueError:
        print("=====================================")
        print("           Invalid input!")
        print("=====================================")
