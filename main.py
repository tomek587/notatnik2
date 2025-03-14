import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from baza import baza


def logowanie():
    login = login_entry.get().strip()
    password = haslo_entry.get().strip()

    if login and password:
        if baza.check_user(login, password):
            otworz_notatnik(login)
        else:
            if not baza.check_user_exists(login):
                baza.insert_user(login, password)
                otworz_notatnik(login)
            else:
                messagebox.showerror(title="Error", message="Podano niepoprawne hasło")
    else:
        messagebox.showerror(title="Error", message="Podaj login i hasło")


def otworz_notatnik(login):
    login_frame.destroy()
    root.geometry("700x350")
    root.configure(bg="#2E2E2E")

    notatnik_frame = tk.Frame(root, bg="#2E2E2E")
    notatnik_frame.pack(pady=20)

    top_frame = tk.Frame(notatnik_frame, bg="#2E2E2E")
    top_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
    tk.Label(top_frame, text=f"Witaj, {login}", font=("Helvetica", 14), bg="#2E2E2E", fg="white").pack(side=tk.LEFT,
                                                                                                       padx=10)
    ttk.Button(top_frame, text="Wyloguj", command=lambda: wyloguj(notatnik_frame)).pack(side=tk.LEFT, padx=10)

    search_entry = tk.Entry(top_frame, width=20, bg="#444444", fg="white")
    search_entry.pack(side=tk.RIGHT, padx=5)
    ttk.Button(top_frame, text="Szukaj",
               command=lambda: wyswietl_notatki(notatki_listbox, login, search_entry.get())).pack(side=tk.RIGHT)

    left_frame = tk.Frame(notatnik_frame, bg="#2E2E2E")
    left_frame.pack(side=tk.LEFT, padx=10)
    notatka_entry = tk.Text(left_frame, height=10, width=30, bg="#444444", fg="white")
    notatka_entry.pack(padx=5, pady=5)

    button_frame = tk.Frame(left_frame, bg="#2E2E2E")
    button_frame.pack(pady=5)

    global add_icon, delete_icon
    add_icon = ImageTk.PhotoImage(Image.open("image/add_btn.png").resize((40, 40)))
    delete_icon = ImageTk.PhotoImage(Image.open("image/delete_btn.jpg").resize((40, 40)))

    tk.Button(button_frame, image=add_icon, bg="#389654",
              command=lambda: dodaj_notatke(notatka_entry, login, notatki_listbox)).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, image=delete_icon, bg="#b83737",
              command=lambda: usun_wybrana_notatka(notatki_listbox, notatka_entry, login)).pack(side=tk.LEFT, padx=5)

    right_frame = tk.Frame(notatnik_frame, bg="#2E2E2E")
    right_frame.pack(side=tk.LEFT, padx=10, anchor='n')
    notatki_listbox = tk.Listbox(right_frame, height=10, width=40, bg="#444444", fg="white", selectbackground="#555555")
    notatki_listbox.pack(padx=5, pady=5)
    notatki_listbox.bind('<<ListboxSelect>>',
                         lambda event: wyswietl_zaznaczona_notatka(notatki_listbox, notatka_entry, login))

    wyswietl_notatki(notatki_listbox, login)


def wyswietl_notatki(notatki_listbox, login, search_term=""):
    notatki_listbox.delete(0, tk.END)

    user_id = baza.get_user_id(login)
    notatki = baza.select_notatki_by_user(user_id)

    if search_term:
        filtered_notatki = [n for n in notatki if search_term in n[1]]
    else:
        filtered_notatki = notatki

    if len(filtered_notatki) == 0:
        if search_term == "":
            notatki_listbox.insert(tk.END, "Brak notatek")
        else:
            notatki_listbox.insert(tk.END, "Brak wyników")
    else:
        for n in filtered_notatki:
            if len(n[1]) > 30:
                display_text = n[1][:33] + '...'
            else:
                display_text = n[1]
            notatki_listbox.insert(tk.END, f"{display_text}  {n[3].strftime('%d-%m-%Y')}")


def wyswietl_zaznaczona_notatka(notatki_listbox, notatka_entry, login):
    selected = notatki_listbox.curselection()

    if len(selected) == 0:
        return
    elif notatki_listbox.get(selected[0]) == "Brak notatek" or notatki_listbox.get(selected[0]) == "Brak wyników":
        return

    user_id = baza.get_user_id(login)
    notatki = baza.select_notatki_by_user(user_id)

    if selected[0] < len(notatki):
        notatka_entry.delete("1.0", tk.END)
        notatka_entry.insert(tk.END, notatki[selected[0]][1])


def dodaj_notatke(notatka_entry, login, notatki_listbox):
    text = notatka_entry.get("1.0", tk.END).strip()
    if text:
        notatka_entry.delete("1.0", tk.END)
        baza.insert_notatka(text, baza.get_user_id(login))
        wyswietl_notatki(notatki_listbox, login)
    else:
        messagebox.showerror("Error", "Notatka nie może być pusta")


def usun_wybrana_notatka(notatki_listbox, notatka_entry, login):
    selected = notatki_listbox.curselection()

    if len(selected) == 0:
        return
    elif notatki_listbox.get(selected[0]) == "Brak notatek" or notatki_listbox.get(selected[0]) == "Brak wyników":
        return

    notatka_id = baza.select_notatki_by_user(baza.get_user_id(login))[selected[0]][0]
    baza.delete_notatka(notatka_id)

    notatka_entry.delete("1.0", tk.END)
    wyswietl_notatki(notatki_listbox, login)


def wyloguj(notatnik_frame):
    notatnik_frame.destroy()
    zaladuj_okno_logowania()


def zaladuj_okno_logowania():
    global login_frame, login_entry, haslo_entry
    root.geometry("300x150")
    root.configure(bg="#2E2E2E")

    login_frame = tk.Frame(root, bg="#2E2E2E")
    login_frame.pack(pady=20)

    tk.Label(login_frame, text="Login:", bg="#2E2E2E", fg="white").grid(row=0, column=0, padx=10, pady=5)

    login_entry = tk.Entry(login_frame, bg="#444444", fg="white")
    login_entry.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(login_frame, text="Hasło:", bg="#2E2E2E", fg="white").grid(row=1, column=0, padx=10, pady=5)

    haslo_entry = tk.Entry(login_frame, show="*", bg="#444444", fg="white")
    haslo_entry.grid(row=1, column=1, padx=10, pady=5)

    ttk.Button(login_frame, text="Zaloguj", command=logowanie).grid(row=2, column=0, columnspan=2, pady=10)


root = tk.Tk()
root.title("Notatnik")
root.iconbitmap("image/icon.ico")
zaladuj_okno_logowania()
root.mainloop()