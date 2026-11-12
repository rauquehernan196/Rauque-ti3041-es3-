from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Producto


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

    def test_admin_dashboard_requires_staff_login(self):
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 302)

        self.client.login(username='Admin1', password='Admin123!')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)

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
