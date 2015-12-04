==========================================
Import Analytic Journal Data data Scenario
==========================================

Imports::

    >>> import datetime
    >>> from dateutil.relativedelta import relativedelta
    >>> from decimal import Decimal
    >>> from operator import attrgetter
    >>> from proteus import config, Model, Wizard
    >>> today = datetime.date.today()

Create database::

    >>> config = config.set_trytond()
    >>> config.pool.test = True

Install analytic_journal module::

    >>> Module = Model.get('ir.module.module')
    >>> analytic_journal_module, = Module.find([('name', '=', 'analytic_journal')])
    >>> Module.install([analytic_journal_module.id], config.context)
    >>> Wizard('ir.module.module.install_upgrade').execute('upgrade')

Create company::

    >>> Currency = Model.get('currency.currency')
    >>> CurrencyRate = Model.get('currency.currency.rate')
    >>> currencies = Currency.find([('code', '=', 'USD')])
    >>> if not currencies:
    ...     currency = Currency(name='US Dollar', symbol=u'$', code='USD',
    ...         rounding=Decimal('0.01'), mon_grouping='[]',
    ...         mon_decimal_point='.')
    ...     currency.save()
    ...     CurrencyRate(date=today + relativedelta(month=1, day=1),
    ...         rate=Decimal('1.0'), currency=currency).save()
    ... else:
    ...     currency, = currencies
    >>> Company = Model.get('company.company')
    >>> Party = Model.get('party.party')
    >>> company_config = Wizard('company.company.config')
    >>> company_config.execute('company')
    >>> company = company_config.form
    >>> party = Party(name='Dunder Mifflin')
    >>> party.save()
    >>> company.party = party
    >>> company.currency = currency
    >>> company_config.execute('add')
    >>> company, = Company.find([])

Reload the context::

    >>> User = Model.get('res.user')
    >>> config._context = User.get_preferences(True, config.context)

Create fiscal year::

    >>> FiscalYear = Model.get('account.fiscalyear')
    >>> Sequence = Model.get('ir.sequence')
    >>> SequenceStrict = Model.get('ir.sequence.strict')
    >>> fiscalyear = FiscalYear(name=str(today.year))
    >>> fiscalyear.start_date = today + relativedelta(month=1, day=1)
    >>> fiscalyear.end_date = today + relativedelta(month=12, day=31)
    >>> fiscalyear.company = company
    >>> post_move_seq = Sequence(name=str(today.year), code='account.move',
    ...     company=company)
    >>> post_move_seq.save()
    >>> fiscalyear.post_move_sequence = post_move_seq
    >>> invoice_seq = SequenceStrict(name=str(today.year),
    ...     code='account.invoice', company=company)
    >>> invoice_seq.save()
    >>> fiscalyear.out_invoice_sequence = invoice_seq
    >>> fiscalyear.in_invoice_sequence = invoice_seq
    >>> fiscalyear.out_credit_note_sequence = invoice_seq
    >>> fiscalyear.in_credit_note_sequence = invoice_seq
    >>> fiscalyear.save()
    >>> FiscalYear.create_period([fiscalyear.id], config.context)

Create chart of accounts::

    >>> AccountTemplate = Model.get('account.account.template')
    >>> Account = Model.get('account.account')
    >>> account_template = AccountTemplate.find([
    ...     ('parent', '=', None),
    ...     ('name', '=', 'Plan General Contable 2008'),
    ...     ])[0]
    >>> create_chart = Wizard('account.create_chart')
    >>> create_chart.execute('account')
    >>> create_chart.form.account_template = account_template
    >>> create_chart.form.company = company
    >>> create_chart.form.account_code_digits = 8
    >>> create_chart.execute('create_account')
    >>> receivable, = Account.find([
    ...         ('kind', '=', 'receivable'),
    ...         ('company', '=', company.id),
    ...         ], limit=1)
    >>> payable, = Account.find([
    ...         ('kind', '=', 'payable'),
    ...         ('company', '=', company.id),
    ...         ], limit=1)
    >>> revenue, = Account.find([
    ...         ('kind', '=', 'revenue'),
    ...         ('company', '=', company.id),
    ...         ], limit=1)
    >>> expense, = Account.find([
    ...         ('kind', '=', 'expense'),
    ...         ('company', '=', company.id),
    ...         ], limit=1)
    >>> create_chart.form.account_receivable = receivable
    >>> create_chart.form.account_payable = payable
    >>> create_chart.execute('create_properties')

Get Tax::

    >>> Tax = Model.get('account.tax')
    >>> tax, = Tax.find([
    ...     ('name', '=', 'IVA 21%'),
    ...     ('group.kind', '=', 'sale'),
    ...     ], limit=1)

Create party::

    >>> Party = Model.get('party.party')
    >>> party = Party(name='Party', code='1234')
    >>> party.save()

Create employee::

    >>> employee_party = Party(name='Eloi', code='1235')
    >>> employee_party.save()
    >>> Employee = Model.get('company.employee')
    >>> employee = Employee()
    >>> employee.party = employee_party
    >>> employee.company = company
    >>> employee.save()

Create works::

    >>> Work = Model.get('timesheet.work')
    >>> project = Work()
    >>> project.name = 'Project'
    >>> project.company = company
    >>> project.save()
    >>> work = Work()
    >>> work.name = 'A111'
    >>> work.company = company
    >>> work.parent = project
    >>> work.timesheet_available = True
    >>> work.save()
    >>> work = Work()
    >>> work.company = company
    >>> work.name = 'A222'
    >>> work.parent = project
    >>> work.timesheet_available = True
    >>> work.save()

Create Day Type::

    >>> DayType = Model.get('timesheet.day_type')
    >>> day_type = DayType()
    >>> day_type.name = 'Normal'
    >>> day_type.save()
    >>> day_type = DayType()
    >>> day_type.name = 'Extra'
    >>> day_type.save()

Create analytic accounts::

    >>> AnalyticAccount = Model.get('analytic_account.account')
    >>> root = AnalyticAccount(type='root', name='Root')
    >>> root.save()
    >>> analytic_account = AnalyticAccount(root=root, parent=root,
    ...     name='Analytic')
    >>> analytic_account.save()

Create product::

    >>> ProductUom = Model.get('product.uom')
    >>> unit, = ProductUom.find([('name', '=', 'Unit')])
    >>> ProductTemplate = Model.get('product.template')
    >>> Product = Model.get('product.product')
    >>> AnalyticSelection = Model.get('analytic_account.account.selection')
    >>> product = Product()
    >>> template = ProductTemplate()
    >>> template.name = 'product'
    >>> template.default_uom = unit
    >>> template.type = 'service'
    >>> template.list_price = Decimal('40')
    >>> template.cost_price = Decimal('25')
    >>> template.account_expense = expense
    >>> template.account_revenue = revenue
    >>> analytic_selection = AnalyticSelection()
    >>> analytic_selection.accounts.append(analytic_account)
    >>> analytic_selection.save()
    >>> template.analytic_accounts = analytic_selection
    >>> template.customer_taxes.append(tax)
    >>> template.save()
    >>> product.template = template
    >>> product.code = 'P1'
    >>> product.save()

Create payment term::

    >>> PaymentTerm = Model.get('account.invoice.payment_term')
    >>> PaymentTermLine = Model.get('account.invoice.payment_term.line')
    >>> payment_term = PaymentTerm(name='Term')
    >>> payment_term_line = PaymentTermLine(type='percent', days=20,
    ...     percentage=Decimal(50))
    >>> payment_term.lines.append(payment_term_line)
    >>> payment_term_line = PaymentTermLine(type='remainder', days=40)
    >>> payment_term.lines.append(payment_term_line)
    >>> payment_term.save()

Create a shipment::

    >>> Shipment = Model.get('catimatge.shipment')
    >>> shipment = Shipment()
    >>> shipment.identifier = '1a'
    >>> shipment.customer_code = '1234'
    >>> shipment.work_code = 'A222'
    >>> shipment.delivery_note = 'C1234'
    >>> shipment.date = today
    >>> shipment.reference = 'P1'
    >>> shipment.record_count = 3
    >>> shipment.save()

Find relations::

    >>> find_relations = Wizard('catimatge.shipment.find_relations', [shipment])
    >>> find_relations.execute('find_relations')
    >>> shipment.product == product
    True
    >>> shipment.party == party
    True

Create invoice::

    >>> find_relations = Wizard('catimatge.shipment.create_invoices', [shipment])
    >>> find_relations.execute('invoices')
    >>> invoice_line, = shipment.invoice_lines
    >>> invoice_line.product == product
    True
    >>> invoice_line.party == party
    True
    >>> invoice_line.quantity
    3.0
    >>> invoice_line.unit_price
    Decimal('40.00000000')
    >>> invoice_line.analytic_accounts.accounts == [analytic_account]
    True

Try to invoice a shipment wihtout related product::

    >>> Shipment = Model.get('catimatge.shipment')
    >>> shipment = Shipment()
    >>> shipment.identifier = '1a'
    >>> shipment.customer_code = '1234'
    >>> shipment.work_code = 'A222'
    >>> shipment.delivery_note = 'C1234'
    >>> shipment.date = today
    >>> shipment.reference = 'P1'
    >>> shipment.record_count = 3
    >>> shipment.save()
    >>> shipment.click('invoice')
    Traceback (most recent call last):
        ...
    UserError: ('UserError', (u'Shipment "1a" has no party set but it is required to invoice it.', ''))
    >>> shipment.party = party
    >>> shipment.click('invoice')
    Traceback (most recent call last):
        ...
    UserError: ('UserError', (u'Shipment "1a" has no product set but it is required to invoice it.', ''))
    >>> shipment.product = product
    >>> shipment.click('invoice')

Create a timesheet::

    >>> Timesheet = Model.get('catimatge.timesheet')
    >>> timesheet = Timesheet()
    >>> timesheet.identifier = '22abc'
    >>> timesheet.headquarter = 'Sabadell'
    >>> timesheet.username = 'Eloi'
    >>> timesheet.start = datetime.datetime.combine(
    ...     today, datetime.time(10, 0, 0))
    >>> timesheet.end = datetime.datetime.combine(
    ...     today, datetime.time(12, 20, 0))
    >>> timesheet.work_code = 'A222'
    >>> timesheet.work_day_type = 'Extra'
    >>> timesheet.operation_type = 'Change piece'
    >>> timesheet.record_count = 3
    >>> timesheet.save()

Find relations::

    >>> find_relations = Wizard('catimatge.timesheet.find_relations',
    ...     [timesheet])
    >>> find_relations.execute('find_relations')
    >>> timesheet.reload()
    >>> timesheet.employee == employee
    True
    >>> timesheet.work.name
    u'A222'
    >>> timesheet.day_type.name
    u'Extra'

Create lines::

    >>> create_lines = Wizard('catimatge.timesheet.create_lines', [timesheet])
    >>> create_lines.execute('create_lines')
    >>> timesheet.reload()
    >>> len(timesheet.timesheet_lines)
    1

