import mysql.connector
from mysql.connector import errorcode
import mdp
import csv


def MySqlConnection():
    try:
      cnx = mysql.connector.connect(user=mdp.BDD_USER, password=mdp.BDD_PASSWORD, host=mdp.BDD_HOST, database='peak_perm')
    except mysql.connector.Error as err:
      if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
      elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
      else:
        print(err)
    else:
        print("connecté")
        return cnx


def MySqlDeconnection(cnx):
    cnx.close()
    print("Connexion mySQL terminée")


def UsersInformation(cnx):
    params = "Select * from users where added = 0 and admin = 0"
    cursor = cnx.cursor()
    cursor.execute(params)
    rows = cursor.fetchall()
    with open('nouv_liste.csv', 'w') as myfile:
        myfile.write('')
    with open('nouv_liste.csv', 'a') as myfile:
        for row in rows:
            print('{0} : {1} - {2} - {3} - {4} - {5} - {6}'.format(row[0], row[1], row[2], row[3], row[4], row[5], row[6]))
            myLine = str(row[1])+';'+str(row[2])+';'+str(row[3])+';'+str(row[5])+'\n'
            myfile.write(myLine)
            UpdateAdded(cnx, row[1])

def UpdateAdded(cnx, login):
    params = "Update users set added = 1 where login ='"+str(login)+"';"
    cursor = cnx.cursor()
    cursor.execute(params)
    cnx.commit()



def getWin(cnx):
    params = "select name from points where pts = (select max(pts) from points)"
    cursor = cnx.cursor()
    cursor.execute(params)
    rows = cursor.fetchall()
    for row in rows:
        return row[0]

def main():
    cnx = MySqlConnection()
    #UsersInformation(cnx)
    UpdateAdded(cnx, 'qrichard')

    MySqlDeconnection(cnx)

main()
