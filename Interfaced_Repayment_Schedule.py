from tkinter import *
from tkinter import ttk

import calendar
import datetime
import os


def calculate():
    total_loan_amount = 0  # общая сумма кредита
    total_interest = 0  # общая выплаченная сумма процентов
    total_payment = 0  # общая сумма выплат (кредит + проценты)

    loan_amount = datatype_check(float, loan_amount_getter.get())
    interest_rate = datatype_check(float, interest_rate_getter.get()) / 100
    term = datatype_check(int, term_getter.get())

    loan_debt = loan_amount
    start_date = datetime.date.today()  # дата получения кредита (текущая дата)
    month = start_date.month  # месяц получения кредита
    year = start_date.year  # год получения кредита

    annual_payment = annuity_payment(loan_amount, interest_rate, term)  # расчет "нормального" ежемесячного платежа
    # (с 1-го до предпоследнего)
    with open('Repayment_schedule.txt', 'w', encoding='utf-8') as file:
        print(file=file)
        print('Дата платежа'.rjust(12), 'Основной долг'.rjust(15), 'Проценты'.rjust(10), 'Платеж'.rjust(10),
              file=file)

        for i in range(term):

            month += 1  # первый платеж в следующем месяце за месяцом получения кредита
            if month > 12:
                month = 1
                year += 1

            repayment_day = start_date.day  # в каждый цикл устанавливаем число платежа согласно первночальному
            # в случае, если условие ниже изменит дату палтежа.
            if repayment_day > calendar.monthrange(year, month)[1]:  # если числа платежа нет в месяце, то
                # в этом месяце платежным устанавливается последний день месяца
                repayment_day = calendar.monthrange(year, month)[1]

            days_year = days_in_year(year)
            days_month = days_in_month(year, month, repayment_day)

            interest = round(loan_debt * (interest_rate / days_year) * days_month, 2)  # сумма процентов в сумме платежа

            loan_repayment = round(annual_payment - interest, 2)  # размер погашения ОД в сумме платежа

            if loan_repayment > loan_debt:
                loan_repayment = loan_debt

            if i == term - 1:  # последний платеж должен быть скорректирован с учетом остатка задолженности
                # для избежания переплаты или недоплаты
                loan_repayment = loan_debt
            else:
                loan_debt -= round(loan_repayment, 2)

            payment = interest + loan_repayment  # Для корректного отображения последнего платежа

            total_loan_amount += loan_repayment
            total_interest += interest
            total_payment += payment
            print(
                str(datetime.date(year, month, repayment_day)).rjust(12),
                str(round(loan_repayment, 2)).rjust(15),
                str(round(interest, 2)).rjust(10),
                str(round(payment, 2)).rjust(10),
                file=file
            )

        print('Всего'.ljust(12), str(round(total_loan_amount, 2)).rjust(15),
              str(round(total_interest, 2)).rjust(10),
              str(round(total_payment, 2)).rjust(10), file=file)
        print(file=file)
        print(f'Ежемесячный платеж: {round(annual_payment, 2)} \nПереплата: {round(total_interest, 2)}', file=file)
        os.startfile('Repayment_schedule.txt')
        if round(total_loan_amount, 2) != round(loan_amount, 2):
            raise ValueError

        for child1 in main_frame.winfo_children():
            child1.grid_remove()

        ready_label = ttk.Label(master=main_frame, text='Готово')
        ready_label.grid(row=1, column=0, columnspan=2)
        ready_button = ttk.Button(master=main_frame, text='Сформировать заново', command=restart)
        ttk.Button(master=main_frame, text='Выйти', command=quit).grid(row=2, column=1)
        ready_button.grid(row=2, column=0)


def datatype_check(datatype, data):
    """Функция осуществляет проверку вводимых данных. В качестве аргумента принимает тип, которому должны
    соответствовать вводимые данные. Возвращает введённые данные (value), если тип данных корректный"""

    try:
        value = datatype(data)
    except ValueError:
        incorrect_value = ttk.Label(master=main_frame, text='Неверные данные')
        incorrect_value.grid(row=0, column=2)
        main_window.mainloop()
    else:
        return value


def annuity_payment(amount, interest_rate, term):
    return round((amount * (interest_rate / 12)) / (1 - (1 + (interest_rate / 12)) ** (-term)), 2)


def days_in_year(year):
    if calendar.isleap(year):
        days_year = 366
    else:
        days_year = 365
    return days_year


def days_in_month(y, m, d):
    """Рассчитывает количество дней между текущим и следующим платежом.
    Переменная month является следующим платежным месяцем"""
    start_date = datetime.date(y, m, d)
    day = start_date.day
    month = start_date.month - 1
    year = start_date.year
    if month < 1:
        month = 12
        year -= 1
    if day > calendar.monthrange(year, month)[1]:
        day = calendar.monthrange(year, month)[1]
    prev_date = datetime.date(year, month, day)
    days_month = int(str(start_date - prev_date).split()[0])
    return days_month


def restart():

    for child1 in main_frame.winfo_children():
        child1.grid_remove()
    ttk.Label(master=main_frame, text='Введите сумму кредита:', font=('Arial', 11)).grid(row=0, column=0, sticky=W)
    ttk.Label(master=main_frame, text='Введите процентную ставку:', font=('Arial', 11)).grid(row=1, column=0, sticky=W)
    ttk.Label(master=main_frame, text='Введите срок кредита:', font=('Arial', 11)).grid(row=2, column=0, sticky=W)

    loan_amount_entry.delete(0, END)
    interest_rate_entry.delete(0, END)
    term_entry.delete(0, END)

    loan_amount_entry.grid(row=0, column=1, sticky=E)
    interest_rate_entry.grid(row=1, column=1, sticky=E)
    term_entry.grid(row=2, column=1, sticky=E)
    ttk.Button(master=main_frame, text='Сформировать график', command=calculate).grid(row=3, column=1, sticky=E)


if __name__ == '__main__':
    main_window = Tk()
    main_window.resizable(width=True, height=True)
    main_window.geometry('500x200+100+50')
    main_window.title('Repayment schedule')

    loan_amount_getter = StringVar()  # получаем сумму кредита из ввода
    interest_rate_getter = StringVar()  # получаем размер % ставки из ввода
    term_getter = StringVar()  # получаем срок из ввода

    # Frames
    main_frame = ttk.Frame(master=main_window, relief=SUNKEN, padding='10')
    main_window.columnconfigure(0, weight=1)
    main_window.rowconfigure(0, weight=1)
    main_frame.grid(row=0, column=0, sticky=(N, W, E, S))

    # Interface objects:
    ttk.Label(master=main_frame, text='Введите сумму кредита:', font=('Arial', 11)).grid(row=0, column=0, sticky=W)
    loan_amount_entry = ttk.Entry(master=main_frame, textvariable=loan_amount_getter)

    loan_amount_entry.grid(row=0, column=1, sticky=E)

    ttk.Label(master=main_frame, text='Введите процентную ставку:', font=('Arial', 11)).grid(row=1, column=0, sticky=W)
    interest_rate_entry = ttk.Entry(master=main_frame, textvariable=interest_rate_getter)

    interest_rate_entry.grid(row=1, column=1, sticky=E)

    ttk.Label(master=main_frame, text='Введите срок кредита:', font=('Arial', 11)).grid(row=2, column=0, sticky=W)
    term_entry = ttk.Entry(master=main_frame, textvariable=term_getter)
    term_entry.insert(0, '')
    term_entry.grid(row=2, column=1, sticky=E)

    ttk.Button(master=main_frame, text='Сформировать график', command=calculate).grid(row=3, column=1, sticky=E)

    for child in main_frame.winfo_children():
        child.grid_configure(padx=5, pady=5)

    main_window.mainloop()
