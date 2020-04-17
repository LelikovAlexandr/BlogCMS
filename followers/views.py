from django.shortcuts import render, redirect
from followers.models import User, Order
from followers.modulbank import get_signature
from dateutil.relativedelta import relativedelta
import requests
from django.utils import timezone
from dotenv import load_dotenv
import os
from followers.instagram import inst
from django.views.generic.edit import UpdateView, DeleteView
from django.urls import reverse_lazy

load_dotenv()


def new_order(request):
    if request.method == 'POST':
        data = request.POST.dict()
        # if get_signature(os.getenv('TEST_SECRET_KEY_MODULBANK'), data) == \
        #         data['signature']:
        user, create = User.objects.update_or_create(
            name=data['client_name'],
        )
        user.email = data['client_email']
        if create:
            start_new_period = timezone.now()
        else:
            start_new_period = max(timezone.now(), user.subscribe_until)
        if data['amount'] == '350':
            user.subscribe_until = start_new_period + relativedelta(
                months=1)
        elif data['amount'] == '1800':
            user.subscribe_until = start_new_period + relativedelta(
                months=6)
        user.save()

        order = Order()
        order.username = User.objects.get(name=data['client_name'])
        order.order_id = data['order_id']
        order.amount = data['amount']
        order.save()
        message = 'OK'
        # else:
        #     message = 'Signature error'
        return render(request, 'followers/order_status.html',
                      context={'message': message})
    else:
        return render(request, 'followers/create_order.html')


def list_of_users(request):
    all_users = User.objects.all()
    return render(request, 'followers/users_list.html',
                  context={'users_list': all_users})


def list_of_orders(request):
    all_orders = Order.objects.all()
    return render(request, 'followers/orders_list.html',
                  context={'orders_list': all_orders})


def get_difference(request):
    set_of_followers = {'digoxin_025', 'katysha_korol', 'lk_mot',
                        'marycake_sweets', 'pryanopek', 'zavarzina.nataly',
                        'anastasia_sentemova', 'zhar_taki', 'ninelrozmanova',
                        'olchik_lucake', 'boris.borisoff', 'hemulsha',
                        'chefcake_club', '_nadyakos_', 'i4ka_i4ka',
                        'prozorovskaya_maria', 'chef_ivanovdenis',
                        'elena.iatskova', 'nina.zhidkova_', 'polinaf1410',
                        'oxanakouznetsova', 'murzaeva_nodira', 'keivy_macaron',
                        'pstfsob', 'liraten999', 'ekaterinavolkovaev',
                        'ok_k_s', 'karamelkamurm', 'natalitort_46',
                        'mona_dolce_casa', 'mintcatnn', 'nota1212018',
                        'katin_hleb', 'troninacake', 'ijuliaf', 'snowyliisa',
                        'i_r_i_n_a_d_v', 'lelikovas', 'semeika74',
                        'nataliaabulgaianova', 'fedotova_mpr',
                        'sladosti_nazarovo', 'vaynberg_nataly', 'darya_aron',
                        'nycksen', 'mariya_vetlitsyna', 'muflon0907',
                        'svetmosina', 'cake_and_flower73',
                        'yaroslavakistanova', 'biros_cake',
                        'svetlana_poltorak82', 'ann.sucre', '__yummy_mummy__',
                        'ramziyadavletova', 'elza.samvelyan', 'krylyschkina',
                        'lubimaya_konditerskaya', 'eska_v', 'anastasialevitan',
                        'kond82', 'tat_zavyalova', 'matkarimova_78',
                        'yanas_patisserie', 'umnov_sergey77', 'rinaalex_07',
                        'renatakancelskiene', 'aaa140484', 'vera.dolcevita',
                        'yanborisova.astra', 'valeriabondarevskaya',
                        'koretskaiaolga6565', 'serenko5917', 'fevraltt.ru',
                        'zefirkikrasnodar', 'chris_cake_kyiv', 'uliy191265',
                        'lelikov.alexandr', 'youlia_tort', 'aiken707',
                        'pizza_ed_io', 'mariia_esyreva',
                        'vanilla_delights_cakes', 'sladkiy_noginsk',
                        'tort_delice', 'susannaargusova', 'alexandr_miller_',
                        'chudo_vypechka', 'dana_diana', 'smorodina.cakes',
                        'magic_cake__', 'tartasal', 'newsvet17', 'ya.em',
                        'irinasharifgal', 'shikarnayaoks',
                        'ekaterinasvetovidova', 'kutuzova7639', 'aerolga',
                        'cakeshop14', 'bordo_ol', 'urbanyulia',
                        'lanakaslivtseva', 'im_from_kamchatka',
                        'anzhelasuponina', 'dessert_nso', 'rusyachef',
                        'pirozhnya', 'tatatihonova93', 'djumihope',
                        'sweetburg', 'dompastry', 'la_tarte_gulyansa',
                        'nataligaynutdinova', 'irishka_orange1', 'julja_lipa',
                        'ingasoldatenkova', 'sila_sveta05', 'instaxsulife',
                        'he.ishere', 'nata_nareira', 'sirovarkino',
                        'jasiawrublewska', 'natal__ia', 'shiryaeva8230',
                        'lyudife3591', 'zevs_dessert', 'irina_cher_ekb',
                        'baking_studio13', 'altuevasvetlana',
                        'vishenka_na_tort_', 'tradition_hleb',
                        'ellachernova5054', 'aleksandra.2413',
                        'lelikova_julia', 'svetachub2807', 'selezneva_ol_ga',
                        'kassiopeya79', 'tatyana710129', 'mari_bakerycake',
                        'choco.grand', 'loys_gr', 'valentusis',
                        'olga_pryaniki', 'allaovch', 'tort_irbit',
                        'lots.sweets', 'tatiana_198303', 'tatyana_picik',
                        'm.zasim', 'valentinafilinkova', 'edimxudeem',
                        'runningonmercury', 'lyubov_selivanova',
                        'melnikpastrychef', 'elena5sam', 'vkusnoyar',
                        'ryban8699', 'shishkina_cake', 'alinochka_seliger',
                        'ga.la9810', 'nad.krasikova', 'mary_shu_tort',
                        'aleksandra.durova', 'rassokhina.cake',
                        'moysladkiyprayn', 'staskova_anastasya',
                        'kseniya___yakovleva', 'virotcenko199', 'pastry_a_r_t',
                        'svetlana_ishaym', 'tanusha_malikova', 'vavi.love',
                        'tanas2727', 'julia.luchinkina', 'irina_kam4atka',
                        'valerica_06', 'elena_elna', 'nemovaindahouse',
                        'dasha_danyasha', 'grebennikovagalina', 'vera_mari28',
                        'galichl', 'utkin_cooking', 'solena', 'mulya2284',
                        'aa.agarkova', 'kapkati', 'lyalka063', 'sasha.bread',
                        'sveta_sha13', 'tatiana.karakal', 'mariiasutiagina1',
                        'irinamussihina', 'almazovalarisa4', 'marina_tsitser',
                        'igolubenkoi', 'maria_rubtsova_',
                        'tatyana_tokareva_spb', 'yamotchka', 'tastycake.ru',
                        'bonbonist', 'pavlova_bakery_coffee', 'chaysuu.cake',
                        'rushana0911', 'vladimir_channov', 'arts_yelena',
                        'ksu4270', 'cakes_by_yana_orel', 'iness.li',
                        'delovkusaem', 'elena_safonova_cakes', 'wwwolya_ya',
                        'janezka_z', 'volkkaterina', 'okdanev', 'kovyrahska',
                        'dinara7276529', 'a_chocolatte', 'gulnarafedorova',
                        'olga1mog', 'elenaelena45678', 'lumierecaks',
                        'eva.sakh', 'simuranvita', 'albinabaraulya',
                        'ekaterinamiroshnikova343', 'myata_cakes', 'yulia_bay',
                        'muhanov.denis', 'kushnerskaya', 'shmik_vika',
                        'olgas.torts', 'hasty_irene', 'easycheesy_nsk',
                        'vkusnoe_delopskov', 'alchemist_of_sweets',
                        'kulinar08', 'alla.mazina', 'inga_osinsyanu',
                        'katya_cat91', 'zinaidakvartnikova',
                        'tanja.podlewskaja', 'snatali_', 'makingabun2018',
                        '_fitbaker_', 'ryabinovie_busy', 'marinosa_',
                        'olesja_muhudinova', 'almira.msk', 'irina_nazarova',
                        'irinamastriuko', 'tatiana_pazhetnykh168',
                        'viktoria_prekrasnaja', 'irinacooking',
                        'chef.with.beard', 'mom_kiki_', 'irinairina5058',
                        'brezhneva__anna', 'irina_dashkovskaya1',
                        'az_desserts_vilnius', 'tortkultura', 'olgaandrosik',
                        'marinika2207', 't_anny33', 'clopcad', 'zulya_tortik',
                        'maliuta.l', 'desert_kiev', 'eli_tort', 'sipbarsa',
                        'tapekser', 'polyakus87', 's.olga69',
                        'sweet_it_simple', 'limonova_ya', 'anna_masevich',
                        'iuliaegorova_', 'l_raskatova_cakes', 'l_i_d_a_kh',
                        'marina_kalashnyk', 'lovedi', 'naida_aduzova',
                        'igra_so_vkusom', 'rodinchef', 'maria_dolek',
                        'ketokemer', 'slada_pryanya', 'annagachich',
                        'elenastarodub2097', 'kakurkina9',
                        '_irisha_sergeevna_', 'gingerbread_fm',
                        'deserti_ot_ledy_di', 'verchenok', 'prudikdasha',
                        'only_my_lips', 'usenko_chef', 'lilksyu',
                        'petuninanton', 'marynakotenko', 'spirinaaspirina',
                        'pisareva_to', 'anastasiya_bairamova', 't.voinova28',
                        'svetabaranovska', 'theapricotbakery_istanbul',
                        'donatovdonat', 'barinova_kuhnya', 'kvittkam',
                        'tea_aet80', 'irina_lakhmanova', 'gkosta0404',
                        'chefvasilev', 'swetly4ok', 'kate_rina_parshina',
                        'strelkovasa', 'margarita_4832', 'elenabakeryvrn',
                        'arsentevairina22', '_vborodina', 'springiwa',
                        'martakutuzovaa', 'magicsheba', 'tawny__owl',
                        'svetlana_kor_p', 'katechuzhik', 'e.podolyan2017',
                        '_cookies_dealer_', 'katua_ar', 'annbelozerskaya',
                        'moymir.1515', 'pensante007', 'put_k_zeli_mechte_',
                        'ksenyaayugova', 'ellen001r', 'lo_ra._',
                        'allakushnir1999a', 'barbareesss', 'ch_laura_',
                        'e_zhukova_tort', 'mariachinalieva', 'svetaznamenski',
                        'cloudberry_salmon', 'tatyana_vkusnyashkina',
                        'olgalazareva74', 'alexandra.klimova75',
                        'ankasalamakhina', 'zi_ma78', 'nata_crazycake',
                        'iakubovarai', 'antonina04.05', 'brightday39',
                        'ilovecake_neru', 'cake_studio_khv_', 'oxana69',
                        'gyuzelwin'}

    set_of_users = set([u.name for u in User.objects.exclude(
        subscribe_until__lte=timezone.now())])
    paid_by_not_followers_set = sorted(
        set(set_of_users) - set(set_of_followers))
    followers_by_not_paid_set = sorted(
        set(set_of_followers) - set(set_of_users))
    paid_by_not_followers = []
    for user in paid_by_not_followers_set:
        paid_by_not_followers.append(User.objects.get(name=user))

    return render(request, 'followers/difference.html', context={
        'paid_by_not_followers': paid_by_not_followers,
        'followers_by_not_paid': followers_by_not_paid_set,
    })


class UserEdit(UpdateView):
    model = User
    fields = ('name', 'subscribe_until',)
    template_name = 'followers/name_edit.html'
    success_url = reverse_lazy('Difference')


class UserDelete(DeleteView):
    model = User
    success_url = reverse_lazy('Users')
