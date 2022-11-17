from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('signup', views.signup, name='signup'),
    path('signin', views.signin, name='signin'),
    path('', views.index, name='index'),
    path('<int:port_id>', views.irasas, name='irasas'),
    path('profilis/<str:username>', views.profilis, name='profilis'),
    path('manoprofilis/<str:pk>/redaguotiprofili', views.redaguotiprofili, name='redaguotiprofili'),
    path('manoprofilis/<str:pk>', views.manoprofilis, name='manoprofilis'),
    path('darboskelbimai', views.skelbimai, name='skelbimai'),
    path('darboskelbimai/<int:skelbimas_id>', views.skelbimas, name='skelbimas'),
    path('pridetiskelbima', views.pridetiskelbima, name='pridetiskelbima'),
    path('darboskelbimai/<int:skelb_id>/aplikavimas', views.aplikavimas, name='aplikavimas'),
    path('manoskelbimai/<str:pk>', views.manoskelbimai, name='manoskelbimai'),
    path('delete_skelbimas/<int:id>', views.delete_skelbimas, name='delete_skelbimas'),
    path('edit_skelbimas/<int:id>', views.edit_skelbimas, name='edit_skelbimas'),
    path('inbox', views.inbox, name='inbox'),
    path('new', views.user_search, name='usersearch'),
    path('new/<username>', views.new_conversation, name='newconversation'),
    path('directs/<username>', views.directs, name='directs'),
    path('send', views.send_direct, name='send_direct'),
    path('like-post', views.like_post, name='like-post'),
    path('follow', views.follow, name='follow'),
    path('<int:port_id>/like', views.like, name='portlike'),
    path('<int:port_id>/favoriteportfolios', views.favorite_port, name='portfavorite'),
    path('darboskelbimai/<int:skelb_id>/favoriteskelbimai', views.favorite_skelb, name='skelbfavorite'),
    path('issaugoti', views.issaugoti, name='issaugoti'),
]