from django.shortcuts import render
from itertools import chain
from operator import attrgetter
from .models import Account, IncomeTransaction, ExpenseTransaction, InnerTransaction
from .forms.IncomeForm import IncomeForm
from .forms.ExpenseForm import ExpenseForm 
from .utils import get_balance, post_income_transaction, post_expense_transaction, get_month, find_nums_in_str, get_income_categories, get_expense_categories
from functools import reduce
import datetime

def main(request):
    # Обработка формы
    formEF = ExpenseForm()
    formIF = IncomeForm()
    if request.method == 'POST':
        if request.POST['form'] == "incf":
            formIF = IncomeForm(request.POST)
        elif request.POST['form'] == "expf":
            formEF = ExpenseForm(request.POST)

        if formIF.is_valid():
            post_income_transaction(formIF.cleaned_data)
            formIF = IncomeForm()
        if formEF.is_valid():
            post_expense_transaction(formEF.cleaned_data)
            formEF = ExpenseForm()

    url_name = request.resolver_match.url_name
    account_list = []

    for account in Account.objects.all():
        account_list.append({
            'name': account.name,
            'amount': get_balance(account)/100
        })
    account_list.insert(0, {
        'name': 'Всего',
        'amount': reduce(
            lambda acc, value: acc + value['amount'],
            account_list,
            0
        )
    })

    return render(request, 'core/main.html', {
        'account_list': account_list,
        'url_name': url_name,
        'income_form': formIF,
        'expence_form': formEF
    })


def report(request):
    url_name = request.resolver_match.url_name
    return render(request, 'core/report.html', {'url_name': url_name})


def history(request):
    url_name = request.resolver_match.url_name
    now = datetime.datetime.now()
    month_filter = now.month
    year_filter = now.year
    income_category = 0
    expense_category = 0

    if request.method == 'POST':
        if request.POST.get('month_filter_history'):
            month_year_filter = request.POST.get('month_filter_history')
            month_year_filter = find_nums_in_str(month_year_filter)
            month_filter = month_year_filter[0]
            year_filter = month_year_filter[1]

            if month_filter in range(1,13):
                incomeT = IncomeTransaction.objects.filter(date__year=year_filter).filter(date__month=month_filter)
                expenseT = ExpenseTransaction.objects.filter(date__year=year_filter).filter(date__month=month_filter)
                innerT = InnerTransaction.objects.filter(date__year=year_filter).filter(date__month=month_filter)
                transactions = sorted((chain(incomeT, expenseT, innerT)), key=attrgetter('date'), reverse=True)
                monthDict = get_month()
                incomeCategoriesDict = get_income_categories()
                expenseCategoriesDict = get_expense_categories()
                return render(
                                request, 'core/history.html',
                                {'url_name': url_name,
                                'transactions': transactions,
                                'month_filter': month_filter,
                                'year_filter': year_filter,
                                'monthDict': monthDict,
                                'income_category': income_category,
                                'incomeCategoriesDict': incomeCategoriesDict,
                                'expense_category': expense_category,
                                'expenseCategoriesDict' : expenseCategoriesDict})
        
        

        if request.POST.get('IncomeTransactionId'):
            IncomeTransactionId=int(request.POST.get('IncomeTransactionId'))
            IncomeTransaction.objects.filter(id=IncomeTransactionId).delete()
        
        if request.POST.get('InnerTransactionId'):
            InnerTransactionId=int(request.POST.get('InnerTransactionId'))
            InnerTransaction.objects.filter(id=InnerTransactionId).delete()

        if request.POST.get('ExpenseTransactionId'):
            ExpenseTransactionId=int(request.POST.get('ExpenseTransactionId'))
            ExpenseTransaction.objects.filter(id=ExpenseTransactionId).delete()

    
    incomeT = IncomeTransaction.objects.filter(date__year=year_filter).filter(date__month=month_filter)
    expenseT = ExpenseTransaction.objects.filter(date__year=year_filter).filter(date__month=month_filter)
    innerT = InnerTransaction.objects.filter(date__year=year_filter).filter(date__month=month_filter)
    transactions = sorted((chain(incomeT, expenseT, innerT)), key=attrgetter('date'), reverse=True)

    monthDict = get_month()
    incomeCategoriesDict = get_income_categories()
    expenseCategoriesDict = get_expense_categories()
    return render(
                    request, 'core/history.html',
                    {'url_name': url_name,
                    'transactions': transactions,
                    'month_filter': month_filter,
                    'year_filter': year_filter,
                    'monthDict': monthDict,
                    'income_category': income_category,
                    'incomeCategoriesDict': incomeCategoriesDict,
                    'expense_category': expense_category,
                    'expenseCategoriesDict' : expenseCategoriesDict})
