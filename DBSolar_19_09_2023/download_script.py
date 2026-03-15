import paramiko
import datetime

def download_file():
    username = 'anujdeshmukh24'
    hostname = f'anujdeshmukh24.ssh.pythonanywhere.com'
    private_key_path = 'C:/Users/deshm/.ssh/id_rsa1'  # Replace with the actual path on your local machine

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(hostname, username=username, key_filename=private_key_path)
        print("Connected successfully")

        # File path on PythonAnywhere and where to save it locally
        remote_file_path = '/home/anujdeshmukh24/DBSolar_19_09_2023/DBSolar_19_09_2023/db.sqlite3'
        local_file_path = f'E:/Production_DB_Backup/db_{datetime.datetime.now().strftime("%Y-%m-%d")}.sqlite3'

        # SFTP session to transfer files
        sftp = ssh.open_sftp()
        sftp.get(remote_file_path, local_file_path)  # Download file
        sftp.close()
        print("File downloaded successfully")

    except paramiko.AuthenticationException as e:
        print(f"Authentication error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    download_file()
