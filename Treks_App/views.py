from django.shortcuts import render
from django.db import connection
from .models import Hiker
from .models import HikerInTrek
from .models import Trek
from .models import TrekInCountry
from datetime import datetime


def dictfetchall(cursor):  # Return all rows from a cursor as a dict
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def index(request):
    # Query the database to retrieve the required data
    with connection.cursor() as cursor:
        cursor.execute("""
        select t.tname
        from Trek t
        """)

        # Pass the data to the template for rendering
        sql_res = dictfetchall(cursor)
    return render(request, 'index.html', {'sql_res': sql_res})


def add_new_hiker(request):
    success = False
    hid_failed = False
    same_country = False
    fatty = False
    context = {
        'success': success,
        'hid_failed': hid_failed,
        'same_country': same_country,
    }
    if request.method == 'POST' and request.POST:
        new_hid = request.POST["hid"]
        new_hname = request.POST["hname"]
        new_country = request.POST["country"]
        if request.POST["smoker"] == "yes":
            new_smoker = True
        if request.POST["smoker"] == "no":
            new_smoker = False
        new_fitness = request.POST["fitness"]
        new_product = Hiker(hid=new_hid, hname=new_hname, country=new_country,
                            smoker=new_smoker, fitness=new_fitness)
        if Hiker.objects.filter(hid=new_hid).exists():
            hid_failed = True
        if not Hiker.objects.filter(country=new_country).exists():
            same_country = True
        if new_smoker and int(new_fitness) < 4:
            fatty = True
        if not (hid_failed or same_country or fatty):
            new_product.save()
            success = True
        context = {
            'success': success,
            'hid_failed': hid_failed,
            'same_country': same_country,
        }
    return render(request, 'add_new_hiker.html', context)


def query_results(request):
    # Query the database to retrieve the required data
    with connection.cursor() as cursor:
        # Query 1
        cursor.execute("""
            select TOP 3 HIT1.tname,COUNT(distinct HIT1.hid) as LoyalHikersNumber
            FROM (select H.hid
            from Hiker H inner join HikerInTrek HIT On H.hid = HIT.hid inner join
            TrekInCountry TIC ON HIT.tname=TIC.tname AND H.country=TIC.country) loyal
            inner join HikerInTrek HIT1 on loyal.hid = HIT1.hid
            group by HIT1.tname
            order by COUNT(distinct HIT1.hid) desc
        """)
        sql_res_1 = dictfetchall(cursor)

        # Query 2
        cursor.execute("""
            select toughcounty.country, MIN(HIT.tdate) as FirstTrip
            from HikerIntrek HIT inner join TrekInCountry TIC2 on HIT.tname = TIC2.tname
            inner join (select TIC.country
            from (select DISTINCT TIC1.country from TrekInCountry TIC1) TIC
                inner join Hiker H on TIC.country = H.country
            group by TIC.country
            HAVING AVG(CAST(H.fitness AS FLOAT)) > 5.8) toughcounty
            on TIC2.country = toughcounty.country
            GROUP BY toughcounty.country
        """)
        sql_res_2 = dictfetchall(cursor)

        # Query 3
        cursor.execute("""
            select TIC1.country, COUNT(DT.tname) AS Count
            from (SELECT TIC.country
                  FROM TrekInCountry TIC
                  GROUP BY TIC.country
                  HAVING COUNT(TIC.tname) >= 2) C LEFT JOIN TrekInCountry TIC1 ON C.country = TIC1.country
            LEFT JOIN (SELECT DISTINCT HIT.hid, HIT.tname
                       FROM Hiker h
            INNER JOIN HikerInTrek HIT ON h.hid = HIT.hid
            INNER JOIN Trek T ON HIT.tname = T.tname
            WHERE h.country = 'Kosovo'
            AND ((h.smoker = 1 AND h.fitness < t.difficulty)
            OR (T.tlength > 100 AND h.fitness < 4))) DT
            ON TIC1.tname = DT.tname
            GROUP BY TIC1.country
            order by Count desc
        """)
        sql_res_3 = dictfetchall(cursor)

    # Pass the data to the template for rendering
    queries = {'sql_res_1': sql_res_1, 'sql_res_2': sql_res_2, 'sql_res_3': sql_res_3}
    return render(request, 'query_results.html', queries)


def Records_Management(request):
    # Query the database to retrieve the required data
    success = False
    hid_failed = False
    tname_failed = False
    hikerdidtrek = False
    fittneslowerthanddef = False
    if request.method == 'POST' and request.POST:
        new_hid = request.POST["hid"]
        new_tname = request.POST["tname"]
        new_tdate = datetime.today().strftime('%Y-%m-%d')
        hiker_exists = Hiker.objects.filter(hid=new_hid).exists()
        trek_exists = Trek.objects.filter(tname=new_tname).exists()
        if not hiker_exists:
            hid_failed = True
        elif not trek_exists:
            tname_failed = True
        elif HikerInTrek.objects.filter(tname=new_tname, hid=new_hid).exists():
            hikerdidtrek = True
        else:
            hiker_fitness = Hiker.objects.filter(hid=new_hid).values_list('fitness', flat=True).first()
            trek_difficulty = Trek.objects.filter(tname=new_tname).values_list('difficulty', flat=True).first()

            if hiker_fitness is not None and trek_difficulty is not None:
                if int(hiker_fitness) < int(trek_difficulty):
                    fittneslowerthanddef = True
        if not (hid_failed or tname_failed or hikerdidtrek or fittneslowerthanddef):
            new_hiker = Hiker.objects.get(hid=new_hid)
            new_Trek = Trek.objects.get(tname=new_tname)
            new_product = HikerInTrek(hid=new_hiker, tname=new_Trek, tdate=new_tdate)
            new_product.save()
            success = True
    with connection.cursor() as cursor:
        cursor.execute("""
        select TOP 10 t.hid, t.tname , t.tdate
        from HikerInTrek t
        ORDER BY tdate DESC, hid ASC
        """)
        # Pass the data to the template for rendering
        sql_res = dictfetchall(cursor)
    recent_registrations = sql_res
    context = {
        'success': success,
        'hid_failed': hid_failed,
        'tname_failed': tname_failed,
        'hikerdidtrek': hikerdidtrek,
        'recent_registrations': recent_registrations,
    }
    return render(request, 'Records_Management.html', context)
