from django.urls import path
from . import views 
from app.views import ProductRegister,ProductList,ProductUpdate,ProductDelete

urlpatterns = [
    path("", views.index, name="index"),
    path('signup/',views.signup, name="signup"),
    path('signin/',views.signin, name="signin"),
    path('userlogout/',views.userlogout, name="userlogout"),
    path('fashionlist/',views.fashionlist, name="fashionlist"),
    path('Grocerylist/',views.Grocerylist, name="Grocerylist"),
    path('Shoeslist/',views.Shoeslist, name="Shoeslist"),
    path('clothslist/',views.clothslist, name="clothslist"),
    path('Mobilelist/',views.Mobilelist, name="Mobilelist"),
    path('searchproduct/',views.searchproduct, name="searchproduct"),
    path('showpricerange/',views.showpricerange, name="showpricerange"),
    path('sortingbyprice/',views.sortingbyprice, name="sortingbyprice"),
    path('showcarts/',views.showcarts, name="showcarts"),
    path('addtocart/<int:productid>',views.addtocart, name="addtocart"),
    path('removecart/<int:productid>',views.removecart, name="removecart"),
    path('updateqty/<int:qv>/<int:productid>',views.updateqty, name="updateqty"),
    path('addaddress/',views.addaddress, name="addaddress"),
    path('showaddress/',views.showaddress, name="showaddress"),
    path('make_payment/',views.make_payment, name="make_payment"),
    path('ProductRegister/',ProductRegister.as_view(), name="ProductRegister"),
    path('ProductList/',views.ProductList, name="ProductList"),
    path('ProductUpdate/<int:pk>',ProductUpdate.as_view(), name="ProductUpdate"),
    path('ProductDelete/<int:pk>',ProductDelete.as_view(), name="ProductDelete"),
]

