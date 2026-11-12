from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Avg, Count, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .forms import (
    ClienteLoginForm,
    ConsultaClienteForm,
    ProductoForm,
    RegistroUsuarioForm,
    UserEditForm,
)
from .models import Producto


def index(request):
    visitas_sesion = request.session.get('visitas_inicio', 0) + 1
    request.session['visitas_inicio'] = visitas_sesion
    productos = Producto.objects.filter(archivado=False).order_by('-id')
    total_productos = Producto.objects.filter(archivado=False).count()
    carrito = request.session.get('carrito', {})
    total_carrito = sum(carrito.values())

    context = {
        'productos': productos,
        'total_productos': total_productos,
        'total_carrito': total_carrito,
        'visitas_sesion': visitas_sesion,
    }
    return render(request, 'Ferreteria/index.html', context)


def consulta_cliente(request):
    if request.method == 'POST':
        form = ConsultaClienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tu consulta fue enviada correctamente. Te contactaremos pronto.')
            return redirect('consulta_cliente')
    else:
        form = ConsultaClienteForm()

    return render(request, 'Ferreteria/consulta_cliente.html', {'form': form})


def catalogo(request):
    productos = Producto.objects.filter(archivado=False).order_by('categoria', 'nombre')
    categorias = list(
        Producto.objects.filter(archivado=False)
        .values_list('categoria', flat=True)
        .distinct()
        .order_by('categoria')
    )
    carrito = request.session.get('carrito', {})
    total_carrito = sum(carrito.values())

    return render(request, 'Ferreteria/catalogo.html', {
        'productos': productos,
        'categorias': categorias,
        'total_productos': productos.count(),
        'total_carrito': total_carrito,
    })


def registro(request):
    if request.user.is_authenticated:
        return redirect('inicio')

    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registro exitoso. Ya puedes comprar en la tienda.')
            return redirect('inicio')
    else:
        form = RegistroUsuarioForm()

    return render(request, 'Ferreteria/registro.html', {'form': form})


def login_cliente(request):
    if request.user.is_authenticated:
        return redirect('inicio')

    if request.method == 'POST':
        form = ClienteLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Bienvenido, {user.username}.')
            return redirect('inicio')
    else:
        form = ClienteLoginForm()

    return render(request, 'Ferreteria/login_cliente.html', {'form': form})


def logout_cliente(request):
    logout(request)
    messages.info(request, 'Sesión cerrada correctamente.')
    return redirect('inicio')


def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id)
    carrito = request.session.get('carrito', {})
    key = str(producto.pk)
    carrito[key] = carrito.get(key, 0) + 1
    request.session['carrito'] = carrito
    request.session.modified = True
    messages.success(request, f'{producto.nombre} fue agregado al carrito.')
    return redirect('inicio')


def quitar_del_carrito(request, producto_id):
    carrito = request.session.get('carrito', {})
    key = str(producto_id)

    if key in carrito:
        if carrito[key] <= 1:
            del carrito[key]
        else:
            carrito[key] -= 1

    request.session['carrito'] = carrito
    request.session.modified = True
    return redirect('carrito')


def carrito(request):
    carrito_data = request.session.get('carrito', {})
    items = []
    total = 0

    for producto_id, cantidad in carrito_data.items():
        producto = Producto.objects.filter(pk=producto_id, archivado=False).first()
        if not producto:
            continue

        subtotal = producto.precio * cantidad
        items.append({
            'producto': producto,
            'cantidad': cantidad,
            'subtotal': subtotal,
        })
        total += subtotal

    cantidad_total = sum(item['cantidad'] for item in items)
    context = {
        'items': items,
        'total': total,
        'cantidad_total': cantidad_total,
    }
    return render(request, 'Ferreteria/carrito.html', context)


@login_required(login_url='login_cliente')
def confirmar_compra(request):
    carrito_data = request.session.get('carrito', {})

    if not carrito_data:
        messages.warning(request, 'Tu carrito está vacío. Agrega productos antes de confirmar la compra.')
        return redirect('carrito')

    request.session['carrito'] = {}
    request.session.modified = True
    messages.success(request, 'Compra confirmada. Tu pedido queda pendiente de preparación y puedes seguir agregando productos.')
    return redirect('carrito')


def login_admin(request):
    if request.user.is_authenticated:
        if request.user.username == 'Admin1' and request.user.is_staff:
            return redirect('admin_dashboard')
        logout(request)
        messages.info(request, 'El acceso administrativo está reservado para Admin1.')

    if request.method == 'POST':
        username = (request.POST.get('username') or '').strip()
        password = request.POST.get('password') or ''

        if username != 'Admin1':
            messages.error(request, 'El panel administrativo solo puede acceder el usuario Admin1.')
            return render(request, 'Ferreteria/login_admin.html')

        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff and user.username == 'Admin1':
            login(request, user)
            messages.success(request, 'Bienvenido al panel administrativo.')
            return redirect('admin_dashboard')

        messages.error(request, 'Credenciales inválidas o no tienes permisos de administrador.')

    return render(request, 'Ferreteria/login_admin.html')


def require_admin1(request):
    if not request.user.is_authenticated or request.user.username != 'Admin1' or not request.user.is_staff:
        logout(request)
        messages.error(request, 'Este panel es exclusivo del usuario Admin1.')
        return redirect('login_admin')
    return None


@login_required(login_url='login_admin')
@staff_member_required(login_url='login_admin')
def admin_dashboard(request):
    redirect_result = require_admin1(request)
    if redirect_result is not None:
        return redirect_result

    productos = Producto.objects.order_by('-id')
    usuarios = User.objects.order_by('-date_joined')
    productos_activos = productos.filter(archivado=False).count()
    productos_archivados = productos.filter(archivado=True).count()
    active_tab = request.GET.get('tab', 'overview')
    if active_tab not in {'overview', 'products', 'users'}:
        active_tab = 'overview'

    return render(request, 'Ferreteria/admin_dashboard.html', {
        'productos': productos,
        'usuarios': usuarios,
        'productos_activos': productos_activos,
        'productos_archivados': productos_archivados,
        'active_tab': active_tab,
    })


@login_required(login_url='login_admin')
@staff_member_required(login_url='login_admin')
def reporte_categorias(request):
    redirect_result = require_admin1(request)
    if redirect_result is not None:
        return redirect_result

    resumen = (
        Producto.objects.values('categoria')
        .annotate(
            cantidad_registros=Count('pk'),
            precio_promedio=Avg('precio'),
            stock_total=Sum('stock'),
        )
        .order_by('categoria')
    )
    return render(request, 'Ferreteria/reporte_categorias.html', {
        'resumen': resumen,
    })


@login_required(login_url='login_admin')
@staff_member_required(login_url='login_admin')
def reporte_stock_critico(request):
    redirect_result = require_admin1(request)
    if redirect_result is not None:
        return redirect_result

    umbral_stock = 5
    productos_criticos = (
        Producto.objects.filter(archivado=False, stock__lte=umbral_stock)
        .order_by('stock', 'categoria', 'nombre')
    )
    return render(request, 'Ferreteria/reporte_stock_critico.html', {
        'productos_criticos': productos_criticos,
        'umbral_stock': umbral_stock,
    })


@login_required(login_url='login_admin')
@staff_member_required(login_url='login_admin')
def product_form(request, pk=None):
    redirect_result = require_admin1(request)
    if redirect_result is not None:
        return redirect_result
    producto = get_object_or_404(Producto, pk=pk) if pk is not None else None
    form = ProductoForm(
        request.POST if request.method == 'POST' else None,
        instance=producto,
    )

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Producto guardado correctamente.')
        return redirect(f"{reverse('admin_dashboard')}?tab=products")

    return render(request, 'Ferreteria/product_form.html', {
        'form': form,
        'producto': producto,
    })


@login_required(login_url='login_admin')
@staff_member_required(login_url='login_admin')
@require_POST
def toggle_archivo(request, pk):
    redirect_result = require_admin1(request)
    if redirect_result is not None:
        return redirect_result

    producto = get_object_or_404(Producto, pk=pk)
    producto.archivado = not producto.archivado
    producto.save()
    estado = 'archivado' if producto.archivado else 'visible'
    messages.success(request, f'El producto quedó {estado} en el feed de compradores.')
    return redirect(f"{reverse('admin_dashboard')}?tab=products")


@login_required(login_url='login_admin')
@staff_member_required(login_url='login_admin')
@require_POST
def delete_producto(request, pk):
    redirect_result = require_admin1(request)
    if redirect_result is not None:
        return redirect_result

    producto = get_object_or_404(Producto, pk=pk)
    producto.delete()
    messages.success(request, 'Producto eliminado correctamente.')
    return redirect(f"{reverse('admin_dashboard')}?tab=products")


@login_required(login_url='login_admin')
@staff_member_required(login_url='login_admin')
def user_form(request, pk):
    redirect_result = require_admin1(request)
    if redirect_result is not None:
        return redirect_result

    usuario = get_object_or_404(User, pk=pk)
    form = UserEditForm(request.POST or None, instance=usuario)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Usuario actualizado correctamente.')
        return redirect('admin_dashboard')

    return render(request, 'Ferreteria/user_form.html', {
        'form': form,
        'usuario': usuario,
    })


@login_required(login_url='login_admin')
@staff_member_required(login_url='login_admin')
@require_POST
def toggle_user(request, pk):
    redirect_result = require_admin1(request)
    if redirect_result is not None:
        return redirect_result

    usuario = User.objects.get(pk=pk)
    if request.user.pk == usuario.pk:
        messages.error(request, 'No puedes desactivar tu propia cuenta de administrador.')
        return redirect('admin_dashboard')

    usuario.is_active = not usuario.is_active
    usuario.save()
    estado = 'activado' if usuario.is_active else 'desactivado'
    messages.success(request, f'Usuario {usuario.username} {estado} correctamente.')
    return redirect('admin_dashboard')


@login_required(login_url='login_admin')
@staff_member_required(login_url='login_admin')
@require_POST
def delete_user(request, pk):
    redirect_result = require_admin1(request)
    if redirect_result is not None:
        return redirect_result

    usuario = User.objects.get(pk=pk)
    if request.user.pk == usuario.pk:
        messages.error(request, 'No puedes eliminar tu propia cuenta de administrador.')
        return redirect('admin_dashboard')

    usuario.delete()
    messages.success(request, 'Usuario eliminado correctamente.')
    return redirect('admin_dashboard')


@login_required(login_url='login_admin')
def logout_admin(request):
    logout(request)
    messages.info(request, 'Sesión cerrada correctamente.')
    return redirect('login_admin')
