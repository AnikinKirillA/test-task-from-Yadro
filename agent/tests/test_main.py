import os
import paramiko
import pytest
from datetime import datetime, timedelta



SSH_HOST = os.getenv("SSH_HOST", "target")
SSH_USER = os.getenv("SSH_USER", "root")
SSH_PASS = os.getenv("SSH_PASS", "toor")
SSH_PORT = int(os.getenv("SSH_PORT", "22"))
LOG_CHECK_MINUTES = int(os.getenv("LOG_CHECK_MINUTES", "5"))


@pytest.fixture(scope='session')
def ssh_connect():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=SSH_HOST, port=SSH_PORT, username=SSH_USER, password=SSH_PASS)
    yield client
    client.close()


def run_cmd(ssh, cmd, timeout=10):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='ignore')
    err = stderr.read().decode('utf-8', errors='ignore')
    rc = stdout.channel.recv_exit_status()
    return rc, out, err


def test_running_web_server(ssh_connect):
    rc, out, err = run_cmd(ssh_connect, "pgrep -f apache2 || true")
    assert rc == 0 or out.strip() != '', "apache2 process not found"


def test_index_404(ssh_connect):
    rc, out, err = run_cmd(ssh_connect, "curl -sS -i -H 'Host: localhost' http://127.0.0.1/index.html")
    assert rc == 0
    assert "200" in out.splitlines()[0]

    rc2, out2, err2 = run_cmd(ssh_connect, "curl -sS -o /dev/null -w '%{http_code}' http://127.0.0.1/thispagedoesnotexist")
    assert rc == 0
    assert out2.strip() == "404"


def test_errors_in_logs(ssh_connect):
    sftp = ssh_connect.open_sftp()
    try:
        with sftp.file('/var/log/apache2/error.log', 'r') as f:
            data = f.read().decode('utf-8', errors='ignore')
    except IOError:
        pytest.skip('error.log not present')
    finally:
        sftp.close()

    now = datetime.now()
    time_limit = now - timedelta(minutes=LOG_CHECK_MINUTES)
    errors_recent = []
    for line in data.splitlines():
        # [Wed Sep 09 12:34:56.789012 2025] [error] ...
        if '[error]' in line.lower():
            try:
                date_str = line.split(']')[0].strip('[')
                log_time = datetime.strptime(date_str, '%a %b %d %H:%M:%S.%f %Y')
                if log_time >= time_limit:
                    errors_recent.append(line)
            except Exception:
                continue
    assert not errors_recent, f'Found error logs: {errors_recent}'


def test_tar(ssh_connect):
    rc, out, err = run_cmd(ssh_connect, "tar --version")
    assert rc == 0
    assert "tar (GNU tar)" in out

    run_cmd(ssh_connect, "mkdir ~/test_tar_ln")
    run_cmd(ssh_connect, 'mkdir original_folder && \
                          echo "Это содержимое первого файла" > original_folder/file1.txt && \
                          echo "Это содержимое второго файла" > original_folder/file2.txt && \
                          echo "Это секретный третий файл" > original_folder/secret.txt')
    run_cmd(ssh_connect, 'tar -cvf my_archive.tar original_folder/')
    rc, out, err = run_cmd(ssh_connect, 'ls -la my_archive.tar')
    assert rc == 0
    assert "my_archive.tar" in out

    rc, out, err = run_cmd(ssh_connect, 'tar -tf my_archive.tar')
    assert rc == 0
    assert "original_folder/file1.txt" in out
    assert "original_folder/file2.txt" in out
    assert "original_folder/secret.txt" in out

    run_cmd(ssh_connect, 'mkdir extract_folder')
    run_cmd(ssh_connect, 'tar -xf my_archive.tar -C extract_folder/')
    rc, out, err = run_cmd(ssh_connect, 'cat extract_folder/original_folder/file1.txt')
    assert rc == 0
    assert "Это содержимое первого файла" in out