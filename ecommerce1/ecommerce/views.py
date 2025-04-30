# imports
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import (
    ListView, DetailView, CreateView,
    UpdateView, DeleteView
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Q
from .models import Product, Category, Wishlist
from .forms import ProductForm, CategoryForm, CustomerCreateForm

class ProductListView(ListView):
    model = Product
    template_name = 'ecommerce/product_list.html'
    context_object_name = 'products'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search')
        category_filter = self.request.GET.get('category')

        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        if category_filter:
            queryset = queryset.filter(category__id=category_filter)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_category'] = self.request.GET.get('category', '')
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'ecommerce/product_detail.html'
    context_object_name = 'product'


def add_to_wishlist(request, product_id):
    if not request.user.is_authenticated:
        return redirect('login')

    product = get_object_or_404(Product, id=product_id)
    Wishlist.objects.get_or_create(user=request.user, product=product)
    return redirect('product_detail', pk=product_id)


def remove_from_wishlist(request, wishlist_item_id):
    item = get_object_or_404(Wishlist, id=wishlist_item_id, user=request.user)
    item.delete()
    return redirect('wishlist_view')


def wishlist_view(request):
    if not request.user.is_authenticated:
        return redirect('login')

    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    return render(request, 'ecommerce/wishlist.html', {'wishlist_items': wishlist_items})


class ProductCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'ecommerce/product_form.html'
    success_url = reverse_lazy('product_list')

    def test_func(self):
        return self.request.user.role == 'ADMIN'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class ProductUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'ecommerce/product_form.html'
    success_url = reverse_lazy('product_list')

    def test_func(self):
        return self.request.user.role == 'ADMIN'


class ProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Product
    template_name = 'ecommerce/product_confirm_delete.html'
    success_url = reverse_lazy('product_list')

    def test_func(self):
        return self.request.user.role == 'ADMIN'


class CategoryCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'ecommerce/category_form.html'
    success_url = reverse_lazy('product_list')

    def test_func(self):
        return self.request.user.role == 'ADMIN'


class SignUpView(CreateView):
    form_class = CustomerCreateForm
    success_url = reverse_lazy('login')
    template_name = 'ecommerce/signup.html'


class LoginView(LoginView):
    template_name = 'ecommerce/login.html'
    redirect_authenticated_user = True


class LogoutView(LogoutView):
    template_name = 'ecommerce/logout.html'
    next_page = reverse_lazy('product_list')

from .forms import CustomerCreateForm

def customer_create_view(request):
    if request.method == 'POST':
        form = CustomerCreateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomerCreateForm()

    return render(request, 'ecommerce/signup_customer.html', {'form': form})