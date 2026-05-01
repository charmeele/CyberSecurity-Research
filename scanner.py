import socket
from threading import Thread
from queue import Queue

# Словарь популярных портов и их сервисов
COMMON_PORTS = {
    21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 
    53: "DNS", 80: "HTTP", 110: "POP3", 143: "IMAP", 
    443: "HTTPS", 445: "SMB", 3306: "MySQL", 3389: "RDP", 8080: "HTTP-Proxy"
}

def scan_port(target, port, queue):
    """Попытка установить соединение с портом."""
    try:
        # Создаем TCP сокет с таймаутом 1 секунда
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((target, port))
        
        if result == 0:
            service = COMMON_PORTS.get(port, "Unknown Service")
            print(f"[+] Порт {port} ОТКРЫТ | Сервис: {service}")
        sock.close()
    except Exception:
        pass

def threader():
    """Функция для многопоточной обработки очереди портов."""
    while True:
        port = q.get()
        if port is None: 
            break
        scan_port(target, port, q)
        q.task_done()

if __name__ == "__main__":
    target = input("Введите IP или домен цели: ")
    try:
        target_ip = socket.gethostbyname(target)
        print(f"[*] Сканирование цели: {target_ip}")
        print("-" * 40)
    except socket.gaierror:
        print("[-] Ошибка: Не удалось разрешить имя хоста.")
        exit()

    # Создаем очередь и запускаем потоки
    q = Queue()
    threads = []
    
    # Создаем 100 потоков для ускорения сканирования
    for i in range(100):
        t = Thread(target=threader)
        t.daemon = True
        t.start()
        threads.append(t)

    # Заполняем очередь портами (от 1 до 1024 — стандартные порты)
    for port in range(1, 1025):
        q.put(port)

    q.join() # Ждем завершения всех задач в очереди

    # Останавливаем потоки
    for i in range(100):
        q.put(None)
    for t in threads:
        t.join()

    print("-" * 40)
    print("[V] Сканирование завершено.")