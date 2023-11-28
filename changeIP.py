import subprocess

def change_hostname(new_hostname):
    try:
        # Zmiana nazwy w pliku /etc/hostname
        subprocess.run(['sudo', 'hostnamectl', 'set-hostname', new_hostname])

        # Modyfikacja nazwy w pliku /etc/hosts
        with open('/etc/hosts', 'r') as file:
            lines = file.readlines()
        
        with open('/etc/hosts', 'w') as file:
            for line in lines:
                if '127.0.1.1' in line:
                    file.write(f'127.0.1.1\t{new_hostname}\n')
                else:
                    file.write(line)
        
        print(f"Pomyślnie zmieniono hostname na {new_hostname}")
    except Exception as e:
        print(f"Wystąpił błąd podczas zmiany hostname: {e}")

# Przykładowe użycie:
nowy_hostname = 'nowy-hostname'  # Tutaj podaj nową nazwę hosta
change_hostname(nowy_hostname)
