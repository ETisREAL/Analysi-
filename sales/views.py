from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Sale
from .forms import SalesSearchForm
from reports.forms import ReportForm
import pandas as pd
from .utils import get_customer_from_id, get_salesman_from_id, get_chart

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.

@login_required
def home_view(request):
    sales_df = None
    positions_df = None
    intermediary_df = None
    positions_df_grouped = None
    merged_df = None
    chart = None
    df = None
    no_data = None

    search_form = SalesSearchForm(request.POST or None)
    report_form = ReportForm()

    if request.method == 'POST':
        date_from = request.POST.get('date_from')
        date_to = request.POST.get('date_to')
        chart_type = request.POST.get('chart_type')
        results_by = request.POST.get('results_by')

        sale_qs = Sale.objects.filter(created__date__lte=date_to, created__date__gte=date_from)
        if len(sale_qs) > 0:
            sales_df = pd.DataFrame(sale_qs.values())
            sales_df['customer_id'] = sales_df['customer_id'].apply(get_customer_from_id)
            sales_df['salesman_id'] = sales_df['salesman_id'].apply(get_salesman_from_id)
            sales_df['created'] = sales_df['created'].apply(lambda x: x.strftime('%Y-%m-%d'))
            sales_df.rename({'customer_id':'customer', 'salesman_id':'salesman', 'id':'sales_id'}, axis=1, inplace=True)

            sales_data = []
            positions_data = []

            
            for sale in sale_qs:
                sale_positions = sale.get_position()
                sales_data.append(sale_positions)

                for pos in sale.get_position():
                    
                    intermediary_positions = pos.query_intermediary_table()
                    intermediary_list = list(intermediary_positions[0].values())
                    # for intermediary_position in intermediary_positions:
                    #     intermediary_table.append(list(intermediary_position.values()))

                    obj = {
                        'position_id': pos.id,
                        'product': pos.product.name,
                        'quantity': pos.quantity,
                        'price': pos.price,
                    }
                    positions_data.append(obj)


            intermediary_df = pd.DataFrame(intermediary_list)
            #intermediary_df.rename({'id': 'intermediary_table_id'}, axis=1, inplace=True) 

            positions_df = pd.DataFrame(positions_data)
            positions_df_grouped = positions_df.groupby('product', as_index=True)[['price', 'quantity']].median()

            merged_df = pd.merge(intermediary_df, positions_df, on='position_id')
            df = merged_df.groupby('sale_id', as_index=True).agg({'position_id': 'last', 'price': 'mean'})

            chart = get_chart(chart_type, sales_df, results_by)

            sales_df = sales_df.to_html()
            intermediary_df = intermediary_df.to_html()
            positions_df_grouped = positions_df_grouped.to_html()
            positions_df = positions_df.to_html()
            merged_df = merged_df.to_html()
            df = df.to_html()
        else:
            no_data = 'No data available in the selected date range'

        
    context = {
        'search_form': search_form,
        'report_form': report_form,
        'sales_df': sales_df,
        'intermediary_df': intermediary_df,
        'positions_df': positions_df,
        'positions_df_grouped': positions_df_grouped,
        'merged_df': merged_df,
        'df': df,
        'chart': chart,
        'no_data': no_data,
    }

    return render(request, 'sales/home.html', context)


class SaleListView(LoginRequiredMixin, ListView):
    model = Sale
    template_name = 'sales/main.html'

""" def sale_list_view(request):
    qs = Sale.objects.all()  #or .filter()
    return (request, 'sales/main.html', {'qs': qs}) """


class SaleDetailView(LoginRequiredMixin, DetailView):
    model = Sale
    template_name = 'sales/detail.html'

""" def sale_detail_view(request, **kwargs):
    pk = kwargs.get('pk')
    obj = Sale.objects.get(pk=pk)
    #or   obj = get_object_or_404(Sale, pk)
    return (render, 'sales/detail.html', {'object_list': obj}) """

