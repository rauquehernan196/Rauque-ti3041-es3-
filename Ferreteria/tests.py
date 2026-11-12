from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from .forms import ConsultaClienteForm
from .models import ConsultaCliente, Producto


class DashboardAndProductsTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='Admin1',
            password='Admin123!',
            is_staff=True,
            is_superuser=True,
        )
        self.active_product = Producto.objects.create(
            nombre='Taladro Percutor',
            categoria='Herramientas Eléctricas',
            precio=39990,
            stock=8,
            archivado=False,
        )
        self.archived_product = Producto.objects.create(
            nombre='Sierra Manual',
            categoria='Herramientas Manuales',
            precio=8990,
            stock=12,
            archivado=True,
        )

    def test_feed_excludes_archived_products(self):
        response = self.client.get(reverse('inicio'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.active_product.nombre)
        self.assertNotContains(response, self.archived_product.nombre)

    def test_home_product_carousel_links_to_each_active_product_cart_button(self):
        response = self.client.get(reverse('inicio'))

        self.assertContains(response, f'href="#producto-compra-{self.active_product.pk}"')
        self.assertContains(response, f'id="producto-compra-{self.active_product.pk}"')
        self.assertNotContains(response, f'href="#producto-compra-{self.archived_product.pk}"')

    def test_customer_consultation_is_saved_and_confirmed(self):
        response = self.client.post(
            reverse('consulta_cliente'),
            {
                'nombre': 'Cliente de prueba',
                'correo': 'cliente@example.com',
                'mensaje': 'Necesito más información sobre este producto.',
                'producto_interes': self.active_product.pk,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('consulta_cliente'), fetch_redirect_response=False)
        consulta = ConsultaCliente.objects.get(correo='cliente@example.com')
        self.assertEqual(consulta.producto_interes, self.active_product)
        self.assertIsNotNone(consulta.fecha)
        response = self.client.get(reverse('consulta_cliente'))
        self.assertContains(response, 'Tu consulta fue enviada correctamente')
        self.assertIn(ConsultaCliente, admin.site._registry)

    def test_consultation_form_rejects_missing_invalid_and_short_fields(self):
        invalid_data = {
            'nombre': 'Jo',
            'correo': 'no-es-un-correo',
            'mensaje': 'Muy corto',
            'producto_interes': '',
        }
        form = ConsultaClienteForm(data=invalid_data)

        self.assertFalse(form.is_valid())
        self.assertIn('nombre', form.errors)
        self.assertIn('correo', form.errors)
        self.assertIn('mensaje', form.errors)
        self.assertFalse(ConsultaCliente.objects.exists())

        response = self.client.post(reverse('consulta_cliente'), invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('nombre', response.context['form'].errors)
        self.assertIn('correo', response.context['form'].errors)
        self.assertIn('mensaje', response.context['form'].errors)
        self.assertFalse(ConsultaCliente.objects.exists())

        missing_fields_form = ConsultaClienteForm(data={})
        self.assertFalse(missing_fields_form.is_valid())
        self.assertIn('nombre', missing_fields_form.errors)
        self.assertIn('correo', missing_fields_form.errors)
        self.assertIn('mensaje', missing_fields_form.errors)

    def test_consultation_post_is_protected_by_csrf(self):
        csrf_client = Client(enforce_csrf_checks=True)
        response = csrf_client.post(reverse('consulta_cliente'), {
            'nombre': 'Cliente de prueba',
            'correo': 'cliente@example.com',
            'mensaje': 'Necesito información sobre herramientas.',
        })

        self.assertEqual(response.status_code, 403)
        self.assertFalse(ConsultaCliente.objects.exists())

    def test_homepage_counts_visits_in_session(self):
        response = self.client.get(reverse('inicio'))
        self.assertEqual(response.context['visitas_sesion'], 1)
        self.assertContains(response, 'Visitas a esta página en esta sesión')

        response = self.client.get(reverse('inicio'))
        self.assertEqual(response.context['visitas_sesion'], 2)

    def test_admin_profile_displays_session_visit_count(self):
        self.client.login(username='Admin1', password='Admin123!')
        self.client.get(reverse('inicio'))

        response = self.client.get(reverse('admin_dashboard'))

        self.assertEqual(response.context['visitas_sesion'], 1)
        self.assertContains(response, 'Visitas al inicio en esta sesión')
        self.assertContains(response, '<strong class="sidebar-session-count">1</strong>')

    def test_admin_dashboard_requires_staff_login(self):
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 302)

        self.client.login(username='Admin1', password='Admin123!')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_homepage_admin_button_opens_custom_dashboard(self):
        self.client.login(username='Admin1', password='Admin123!')

        response = self.client.get(reverse('inicio'))

        self.assertContains(response, f'href="{reverse("admin_dashboard")}"')
        self.assertNotContains(response, 'href="/admin/"')

    def test_store_logo_and_name_link_to_home_from_every_module(self):
        self.client.login(username='Admin1', password='Admin123!')
        pages = [
            ('inicio', [], 'brand'),
            ('catalogo', [], 'brand'),
            ('carrito', [], 'brand'),
            ('consulta_cliente', [], 'brand'),
            ('reporte_categorias', [], 'brand'),
            ('reporte_stock_critico', [], 'brand'),
            ('login_cliente', [], 'auth-brand'),
            ('login_admin', [], 'admin-auth-brand'),
            ('registro', [], 'auth-brand'),
            ('admin_dashboard', [], 'sidebar-brand'),
            ('producto_nuevo', [], 'sidebar-brand'),
            ('usuario_editar', [self.user.pk], 'sidebar-brand'),
        ]

        for route_name, route_args, brand_class in pages:
            with self.subTest(page=route_name):
                page_client = Client() if brand_class in {
                    'auth-brand',
                    'admin-auth-brand',
                } else self.client
                response = page_client.get(reverse(route_name, args=route_args))
                self.assertEqual(response.status_code, 200)
                self.assertContains(
                    response,
                    f'<a class="{brand_class}" href="{reverse("inicio")}"',
                )

    def test_admin_can_create_edit_and_delete_products_from_dashboard(self):
        self.client.login(username='Admin1', password='Admin123!')
        product_list_url = f"{reverse('admin_dashboard')}?tab=products"

        response = self.client.post(
            reverse('producto_nuevo'),
            {
                'nombre': 'Llave ajustable',
                'categoria': 'Herramientas',
                'precio': 12500,
                'stock': 6,
                'imagen': '',
            },
        )
        self.assertRedirects(response, product_list_url)
        product = Producto.objects.get(nombre='Llave ajustable')

        response = self.client.get(product_list_url)
        self.assertEqual(response.context['active_tab'], 'products')
        self.assertContains(response, product.nombre)
        self.assertContains(response, "return confirm('¿Deseas eliminar este producto?')")

        response = self.client.post(
            reverse('producto_editar', args=[product.pk]),
            {
                'nombre': 'Llave ajustable reforzada',
                'categoria': 'Herramientas',
                'precio': 14990,
                'stock': 4,
                'imagen': '',
            },
        )
        self.assertRedirects(response, product_list_url)
        product.refresh_from_db()
        self.assertEqual(product.nombre, 'Llave ajustable reforzada')
        self.assertEqual(product.precio, 14990)

        delete_url = reverse('producto_eliminar', args=[product.pk])
        response = self.client.get(delete_url)
        self.assertEqual(response.status_code, 405)
        self.assertTrue(Producto.objects.filter(pk=product.pk).exists())

        response = self.client.post(delete_url)
        self.assertRedirects(response, product_list_url)
        self.assertFalse(Producto.objects.filter(pk=product.pk).exists())
        response = self.client.get(product_list_url)
        self.assertNotContains(response, 'Llave ajustable reforzada')

    def test_category_report_uses_database_aggregations(self):
        Producto.objects.create(
            nombre='Taladro compacto',
            categoria='Herramientas Eléctricas',
            precio=10000,
            stock=2,
        )
        self.client.login(username='Admin1', password='Admin123!')

        response = self.client.get(reverse('reporte_categorias'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Ferreteria/reporte_categorias.html')
        self.assertTemplateUsed(response, 'Ferreteria/base.html')
        summary = next(
            row for row in response.context['resumen']
            if row['categoria'] == 'Herramientas Eléctricas'
        )
        self.assertEqual(summary['cantidad_registros'], 2)
        self.assertEqual(summary['precio_promedio'], 24995)
        self.assertEqual(summary['stock_total'], 10)
        self.assertContains(response, 'Stock crítico')

    def test_critical_stock_report_filters_and_orders_active_products(self):
        Producto.objects.create(
            nombre='Llave con poco stock',
            categoria='Herramientas',
            precio=5000,
            stock=3,
        )
        Producto.objects.create(
            nombre='Producto agotado',
            categoria='Herramientas',
            precio=3000,
            stock=0,
        )
        Producto.objects.create(
            nombre='Archivado con poco stock',
            categoria='Herramientas',
            precio=4000,
            stock=1,
            archivado=True,
        )
        self.client.login(username='Admin1', password='Admin123!')

        response = self.client.get(reverse('reporte_stock_critico'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Ferreteria/reporte_stock_critico.html')
        self.assertEqual(response.context['umbral_stock'], 5)
        products = list(response.context['productos_criticos'])
        self.assertEqual(
            [product.nombre for product in products],
            ['Producto agotado', 'Llave con poco stock'],
        )
        self.assertContains(response, 'Productos activos con existencias iguales o menores a 5')
        self.assertNotContains(response, 'Archivado con poco stock')

    def test_inventory_reports_require_admin_login(self):
        for report_name in ('reporte_categorias', 'reporte_stock_critico'):
            with self.subTest(report=report_name):
                response = self.client.get(reverse(report_name))
                self.assertEqual(response.status_code, 302)
                self.assertIn('/login/', response.url)

    def test_only_admin1_can_access_admin_panel(self):
        get_user_model().objects.filter(username='Admin1').delete()
        get_user_model().objects.create_user(
            username='Admin1',
            password='Admin123!',
            is_staff=True,
            is_superuser=True,
        )
        other_admin = get_user_model().objects.create_user(
            username='OtroAdmin',
            password='Password123!',
            is_staff=True,
        )

        self.client.login(username='OtroAdmin', password='Password123!')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

        self.client.logout()
        self.client.login(username='Admin1', password='Admin123!')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_customers_can_register_and_add_items_to_cart(self):
        response = self.client.post(
            reverse('registro'),
            {
                'username': 'cliente',
                'email': 'cliente@correo.com',
                'password1': 'Clave123!',
                'password2': 'Clave123!',
            },
        )
        self.assertEqual(response.status_code, 302)

        self.client.login(username='cliente', password='Clave123!')
        response = self.client.post(reverse('agregar_al_carrito', args=[self.active_product.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(self.active_product.pk), self.client.session.get('carrito', {}))

    def test_adding_products_keeps_catalog_open_and_updates_cart_count(self):
        catalog_url = reverse('catalogo')
        catalog_referer = f'http://testserver{catalog_url}'
        add_url = reverse('agregar_al_carrito', args=[self.active_product.pk])

        for expected_quantity in (1, 2):
            response = self.client.get(add_url, HTTP_REFERER=catalog_referer)
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.url, catalog_referer)

            response = self.client.get(catalog_url)
            article_label = 'artículo' if expected_quantity == 1 else 'artículos'
            self.assertContains(
                response,
                f'<span class="cart-count" aria-hidden="true">{expected_quantity}</span>',
            )
            self.assertContains(
                response,
                f'aria-label="Carrito de compras: {expected_quantity} {article_label}"',
            )

        response = self.client.get(reverse('carrito'))
        self.assertContains(response, self.active_product.nombre)
        self.assertContains(response, '<strong>2</strong>')

    def test_adding_product_rejects_external_referer_redirects(self):
        response = self.client.get(
            reverse('agregar_al_carrito', args=[self.active_product.pk]),
            HTTP_REFERER='https://example.org/outside',
        )

        self.assertRedirects(response, reverse('inicio'), fetch_redirect_response=False)

    def test_confirmar_compra_requires_login(self):
        response = self.client.post(reverse('confirmar_compra'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/cuenta/login/', response.url)

    def test_admin_can_edit_registered_users(self):
        cliente = get_user_model().objects.create_user(
            username='cliente_editable',
            password='Password123!',
            email='cliente@correo.com',
            is_staff=False,
        )

        self.client.login(username='Admin1', password='Admin123!')
        response = self.client.get(reverse('usuario_editar', args=[cliente.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Editar usuario')

    def test_catalog_shows_all_active_products_with_images(self):
        Producto.objects.all().delete()
        productos = [
            Producto(
                nombre=f'Producto {i}',
                categoria='Herramientas',
                precio=1000 + i,
                stock=10 + i,
                imagen=f'https://images.unsplash.com/photo-1{i}?auto=format&fit=crop&w=900&q=80',
                archivado=False,
            )
            for i in range(40)
        ]
        Producto.objects.bulk_create(productos)

        response = self.client.get(reverse('catalogo'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['productos']), 40)
        self.assertContains(response, 'Producto 0')
        self.assertContains(response, 'https://images.unsplash.com')
