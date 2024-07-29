from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate , login , logout
from django.http import HttpResponseRedirect,HttpResponse
from .models import profile
from django.contrib.auth.decorators import login_required
from .form import UploadImageForm
from .models import Image,Disease
import tensorflow as tf
from keras.models import load_model
import numpy as np
import pickle
import pandas as pd
from sklearn.impute import SimpleImputer
import sklearn
from django.conf import settings
from joblib import load
from django.utils.safestring import mark_safe



model = load_model(r'accounts\\Models\\disease_detection.keras')
# Create your views here.
def home(request):
    return render(request,'index.html')

# Create your views here.
def register(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        c_password = request.POST.get('Cpassword')
        user_obj = User.objects.filter(username = email)

        if password != c_password:
            messages.warning(request, "Password does'nt matches")
            return HttpResponseRedirect(request.path_info)

        if user_obj.exists():
            messages.warning(request, 'Email is already taken.')
            return HttpResponseRedirect(request.path_info)

        print(email)

        user_obj = User.objects.create(first_name = username , email = email , username = email)
        user_obj.set_password(password)
        user_obj.save()

        messages.success(request, 'Successfully Registered.')
        return HttpResponseRedirect(request.path_info)


    return render(request ,'regis.html')


def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user_obj = User.objects.filter(username=email)

        if not user_obj.exists():
            messages.warning(request, 'Account not found.')
            return HttpResponseRedirect(request.path_info)

        user_obj = authenticate(username=email, password=password)
        if user_obj:
            login(request, user_obj)
            return redirect('/')
        messages.warning(request, 'Invalid credentials')
        return HttpResponseRedirect(request.path_info)

    return render(request, 'login.html')

@login_required
def logout_view(request):
    logout(request)
    # Optionally add logic here, e.g., messages or redirects
    return redirect('/')

@login_required
def upload(request):
    return render(request, 'upload.html')

@login_required
def type(request):
    return render(request, 'plant_type.html')

@login_required
def board(request):
    diseases = Disease.objects.filter(image__user=request.user)
    user = request.user
    return render(request, 'dashbord.html', {'diseases': diseases,'user':user})


class_names = ['Apple : Apple scab', 'Apple : Black rot', 'Apple : Cedar rust', 'Apple : Healthy',
               'Corn : Gray leaf spot', 'Corn : Common rust', 'Corn : Northern Leaf Blight', 'Corn : Healthy',
               'Grape : Black rot', 'Grape : Black Measles',  'Grape : Isariopsis Leaf Spot','Grape : Healthy',
               'Potato : Early blight',  'Potato : Late blight','Potato : Healthy',
               'Tomato : Bacterial spot', 'Tomato : Early blight', 'Tomato : Late blight', 'Tomato : Leaf Mold', 'Tomato : Yellow leaf curl virus', 'Tomato : Healthy'
               ]

def preprocess_image(image_path):
    img = tf.keras.preprocessing.image.load_img(image_path, target_size=(256, 256))
    img_array = tf.keras.preprocessing.image.img_to_array(img)
    img_array = tf.expand_dims(img_array, 0)  # Create batch axis
    return img_array

def upload_image( request):
    if request.method == 'POST':
        form = UploadImageForm(request.POST, request.FILES)
        if form.is_valid():
            image_file = form.cleaned_data['image']
            image_name = image_file.name  # Generate a unique filename (optional)


            # Save image to database (assuming 'Image' model is defined)
            user = request.user
            image = Image(user = user,image=image_file)
            image.save()
            image_name.replace(' ', '-')
            image_path = f'public\\static\\disease_images\\{image_name}'
            image_array = preprocess_image(image_path)
            print("IMAGE PATH IS :",image_path)
            predictions = model.predict(image_array)
            predicted_class_index = np.argmax(predictions[0])
            predicted_class = class_names[predicted_class_index]
            disease = Disease(disease=predicted_class, image=image)
            disease.save()
            disease_id = disease.id
            disease = Disease.objects.get(pk=disease_id)
            image_url = disease.image.image.url


            return render(request, 'upload.html' ,  {'predicted_disease': predicted_class, 'url': image_url})
    else:
        form = UploadImageForm()

    return render(request, 'upload.html', {'form': form})

def Crop_Recommendation(request):
    recommended_crop = ''
    if request.method == 'POST':
        nitrogen=request.POST.get('nitrogen')
        phosphorus = request.POST.get('phosphorus')
        potassium = request.POST.get('potassium')
        temperature = request.POST.get('temperature')
        humidity = request.POST.get('humidity')
        phLevel = request.POST.get('phLevel')
        rainfall = request.POST.get('rainfall')

        RF_joblib = r'accounts\\Models\\RandomForest.joblib'
        loaded_RF_model = load(RF_joblib)
        new_data = np.array([[nitrogen, phosphorus, potassium, temperature, humidity, phLevel, rainfall]])
        recommended_crop = loaded_RF_model.predict(new_data)
        recommended_crop = recommended_crop[0]

    return render(request, 'crop_rec.html',{'crop': recommended_crop})

def Fertilizer_Recommendation(request):
    recommendation = ''

    if request.method == 'POST':
        crop_name = request.POST.get('crop')
        N = int(request.POST.get('nitrogen'))
        P = int(request.POST.get('phosphorus'))
        K = int(request.POST.get('potassium'))

        df = pd.read_csv(r'accounts\\Fertilizer Recommendation.csv')

        nr = df[df['Crop'] == crop_name]['N'].iloc[0]
        pr = df[df['Crop'] == crop_name]['P'].iloc[0]
        kr = df[df['Crop'] == crop_name]['K'].iloc[0]

        n = nr - N
        p = pr - P
        k = kr - K

        temp = {abs(n): "N", abs(p): "P", abs(k): "K"}
        fertilizer_dic = {
            'NHigh': """The N value of soil is high and might give rise to weeds.
                <br/> Please consider the following suggestions:

                <br/><br/> 1. <i> Manure </i> – adding manure is one of the simplest ways to amend your soil with nitrogen. Be careful as there are various types of manures with varying degrees of nitrogen.

                <br/> 2. <i>Coffee grinds </i> – use your morning addiction to feed your gardening habit! Coffee grinds are considered a green compost material which is rich in nitrogen. Once the grounds break down, your soil will be fed with delicious, delicious nitrogen. An added benefit to including coffee grounds to your soil is while it will compost, it will also help provide increased drainage to your soil.

                <br/>3. <i>Plant nitrogen fixing plants</i> – planting vegetables that are in Fabaceae family like peas, beans and soybeans have the ability to increase nitrogen in your soil

                <br/>4. Plant ‘green manure’ crops like cabbage, corn and brocolli

                <br/>5. <i>Use mulch (wet grass) while growing crops</i> - Mulch can also include sawdust and scrap soft woods""",

            'Nlow': """The N value of your soil is low.
                <br/> Please consider the following suggestions:
                <br/><br/> 1. <i>Add sawdust or fine woodchips to your soil</i> – the carbon in the sawdust/woodchips love nitrogen and will help absorb and soak up and excess nitrogen.

                <br/>2. <i>Plant heavy nitrogen feeding plants</i> – tomatoes, corn, broccoli, cabbage and spinach are examples of plants that thrive off nitrogen and will suck the nitrogen dry.

                <br/>3. <i>Water</i> – soaking your soil with water will help leach the nitrogen deeper into your soil, effectively leaving less for your plants to use.

                <br/>4. <i>Sugar</i> – In limited studies, it was shown that adding sugar to your soil can help potentially reduce the amount of nitrogen is your soil. Sugar is partially composed of carbon, an element which attracts and soaks up the nitrogen in the soil. This is similar concept to adding sawdust/woodchips which are high in carbon content.

                <br/>5. Add composted manure to the soil.

                <br/>6. Plant Nitrogen fixing plants like peas or beans.

                <br/>7. <i>Use NPK fertilizers with high N value.

                <br/>8. <i>Do nothing</i> – It may seem counter-intuitive, but if you already have plants that are producing lots of foliage, it may be best to let them continue to absorb all the nitrogen to amend the soil for your next crops.""",

            'PHigh': """The P value of your soil is high.
                <br/> Please consider the following suggestions:

                <br/><br/>1. <i>Avoid adding manure</i> – manure contains many key nutrients for your soil but typically including high levels of phosphorous. Limiting the addition of manure will help reduce phosphorus being added.

                <br/>2. <i>Use only phosphorus-free fertilizer</i> – if you can limit the amount of phosphorous added to your soil, you can let the plants use the existing phosphorus while still providing other key nutrients such as Nitrogen and Potassium. Find a fertilizer with numbers such as 10-0-10, where the zero represents no phosphorous.

                <br/>3. <i>Water your soil</i> – soaking your soil liberally will aid in driving phosphorous out of the soil. This is recommended as a last ditch effort.

                <br/>4. Plant nitrogen fixing vegetables to increase nitrogen without increasing phosphorous (like beans and peas).

                <br/>5. Use crop rotations to decrease high phosphorous levels""",

            'Plow': """The P value of your soil is low.
                <br/> Please consider the following suggestions:

                <br/><br/>1. <i>Bone meal</i> – a fast acting source that is made from ground animal bones which is rich in phosphorous.

                <br/>2. <i>Rock phosphate</i> – a slower acting source where the soil needs to convert the rock phosphate into phosphorous that the plants can use.

                <br/>3. <i>Phosphorus Fertilizers</i> – applying a fertilizer with a high phosphorous content in the NPK ratio (example: 10-20-10, 20 being phosphorous percentage).

                <br/>4. <i>Organic compost</i> – adding quality organic compost to your soil will help increase phosphorous content.

                <br/>5. <i>Manure</i> – as with compost, manure can be an excellent source of phosphorous for your plants.

                <br/>6. <i>Clay soil</i> – introducing clay particles into your soil can help retain & fix phosphorus deficiencies.

                <br/>7. <i>Ensure proper soil pH</i> – having a pH in the 6.0 to 7.0 range has been scientifically proven to have the optimal phosphorus uptake in plants.

                <br/>8. If soil pH is low, add lime or potassium carbonate to the soil as fertilizers. Pure calcium carbonate is very effective in increasing the pH value of the soil.

                <br/>9. If pH is high, addition of appreciable amount of organic matter will help acidify the soil. Application of acidifying fertilizers, such as ammonium sulfate, can help lower soil pH""",

            'KHigh': """The K value of your soil is high</b>.
                <br/> Please consider the following suggestions:

                <br/><br/>1. <i>Loosen the soil</i> deeply with a shovel, and water thoroughly to dissolve water-soluble potassium. Allow the soil to fully dry, and repeat digging and watering the soil two or three more times.

                <br/>2. <i>Sift through the soil</i>, and remove as many rocks as possible, using a soil sifter. Minerals occurring in rocks such as mica and feldspar slowly release potassium into the soil slowly through weathering.

                <br/>3. Stop applying potassium-rich commercial fertilizer. Apply only commercial fertilizer that has a '0' in the final number field. Commercial fertilizers use a three number system for measuring levels of nitrogen, phosphorous and potassium. The last number stands for potassium. Another option is to stop using commercial fertilizers all together and to begin using only organic matter to enrich the soil.

                <br/>4. Mix crushed eggshells, crushed seashells, wood ash or soft rock phosphate to the soil to add calcium. Mix in up to 10 percent of organic compost to help amend and balance the soil.

                <br/>5. Use NPK fertilizers with low K levels and organic fertilizers since they have low NPK values.

                <br/>6. Grow a cover crop of legumes that will fix nitrogen in the soil. This practice will meet the soil’s needs for nitrogen without increasing phosphorus or potassium.
                """,

            'Klow': """The K value of your soil is low.
                <br/>Please consider the following suggestions:

                <br/><br/>1. Mix in muricate of potash or sulphate of potash
                <br/>2. Try kelp meal or seaweed
                <br/>3. Try Sul-Po-Mag
                <br/>4. Bury banana peels an inch below the soils surface
                <br/>5. Use Potash fertilizers since they contain high values potassium
                """
        }
        max_value = temp[max(temp.keys())]
        if max_value == "N":
            if n < 0:
                key = 'NHigh'
            else:
                key = "Nlow"
        elif max_value == "P":
            if p < 0:
                key = 'PHigh'
            else:
                key = "Plow"
        else:
            if k < 0:
                key = 'KHigh'
            else:
                key = "Klow"

        print(key)

        recommendation = mark_safe(fertilizer_dic[key])

    return render(request,'fert_rec.html',{'recommendation': recommendation})


def pest_rec(request,Did):
    diseases = Disease.objects.get(id = Did)
    disease_dic = {
        'Apple : Apple scab': """ <b>Crop</b>: Apple <br/>Disease: Apple Scab<br/>
            <br/> Cause of disease:

            <br/><br/> 1. Apple scab overwinters primarily in fallen leaves and in the soil. Disease development is favored by wet, cool weather that generally occurs in spring and early summer.

            <br/> 2. Fungal spores are carried by wind, rain or splashing water from the ground to flowers, leaves or fruit. During damp or rainy periods, newly opening apple leaves are extremely susceptible to infection. The longer the leaves remain wet, the more severe the infection will be. Apple scab spreads rapidly between 55-75 degrees Fahrenheit.
            <br/><br/> How to prevent/cure the disease <br/>
            <br/>1. Choose resistant varieties when possible.

            <br/>2. Rake under trees and destroy infected leaves to reduce the number of fungal spores available to start the disease cycle over again next spring

            <br/>3. Water in the evening or early morning hours (avoid overhead irrigation) to give the leaves time to dry out before infection can occur.
            <br/>4. Spread a 3- to 6-inch layer of compost under trees, keeping it away from the trunk, to cover soil and prevent splash dispersal of the fungal spores.""",

        'Apple : Black rot': """ <b>Crop</b>: Apple <br/>Disease: Black Rot<br/>
            <br/> Cause of disease:

            <br/><br/>Black rot is caused by the fungus Diplodia seriata (syn Botryosphaeria obtusa).The fungus can infect dead tissue as well as living trunks, branches, leaves and fruits. In wet weather, spores are released from these infections and spread by wind or splashing water. The fungus infects leaves and fruit through natural openings or minor wounds.
            <br/><br/> How to prevent/cure the disease <br/>
            <br/>1. Prune out dead or diseased branches.

            <br/>2. Prune out dead or diseased branches.

            <br/>3. Remove infected plant material from the area.
            <br/>4. Remove infected plant material from the area.
            <br/>5. Be sure to remove the stumps of any apple trees you cut down. Dead stumps can be a source of spores.""",

        'Apple : Cedar rust': """ <b>Crop</b>: Apple <br/>Disease: Cedar Apple Rust<br/>
            <br/> Cause of disease:

            <br/><br/>Cedar apple rust (Gymnosporangium juniperi-virginianae) is a fungal disease that depends on two species to spread and develop. It spends a portion of its two-year life cycle on Eastern red cedar (Juniperus virginiana). The pathogen’s spores develop in late fall on the juniper as a reddish brown gall on young branches of the trees.

            <br/><br/> How to prevent/cure the disease <br/>
            <br/>1. Since the juniper galls are the source of the spores that infect the apple trees, cutting them is a sound strategy if there aren’t too many of them.

            <br/>2. While the spores can travel for miles, most of the ones that could infect your tree are within a few hundred feet.

            <br/>3. The best way to do this is to prune the branches about 4-6 inches below the galls.""",

        'Apple : Healthy': """ <b>Crop</b>: Apple <br/>Disease: No disease<br/>

            <br/><br/> The crop is healthy!!!""",

        'Corn : Gray leaf spot': """ <b>Crop</b>: Corn <br/>Disease: Grey Leaf Spot<br/>
            <br/> Cause of disease:

            <br/><br/>Gray leaf spot lesions on corn leaves hinder photosynthetic activity, reducing carbohydrates allocated towards grain fill. The extent to which gray leaf spot damages crop yields can be estimated based on the extent to which leaves are infected relative to grainfill. Damage can be more severe when developing lesions progress past the ear leaf around pollination time.	Because a decrease in functioning leaf area limits photosynthates dedicated towards grainfill, the plant might mobilize more carbohydrates from the stalk to fill kernels.


            <br/><br/> How to prevent/cure the disease <br/>
            <br/>1. In order to best prevent and manage corn grey leaf spot, the overall approach is to reduce the rate of disease growth and expansion.

            <br/>2. This is done by limiting the amount of secondary disease cycles and protecting leaf area from damage until after corn grain formation.

            <br/>3. High risk factors for grey leaf spot in corn: <br/>
                        a.	Susceptible hybrid
                        b.	Continuous corn
                        c.	Late planting date
                        d.	Minimum tillage systems
                        e.	Field history of severe disease
                        f.	Early disease activity (before tasseling)
                        g.	Irrigation
                        h.	Favorable weather forecast for disease.""",

        'Corn : Common rust': """ <b>Crop</b>: Corn <br/>Disease: Common Rust<br/>
            <br/> Cause of disease:

            <br/><br/>Common corn rust, caused by the fungus Puccinia sorghi, is the most frequently occurring of the two primary rust diseases of corn in the U.S., but it rarely causes significant yield losses in Ohio field (dent) corn. Occasionally field corn, particularly in the southern half of the state, does become severely affected when weather conditions favor the development and spread of rust fungus

            <br/><br/> How to prevent/cure the disease <br/>
            <br/>1. Although rust is frequently found on corn in Ohio, very rarely has there been a need for fungicide applications. This is due to the fact that there are highly resistant field corn hybrids available and most possess some degree of resistance.

            <br/>2. However, popcorn and sweet corn can be quite susceptible. In seasons where considerable rust is present on the lower leaves prior to silking and the weather is unseasonably cool and wet, an early fungicide application may be necessary for effective disease control. Numerous fungicides are available for rust control. """,

        'Corn : Healthy': """ <b>Crop</b>: Corn(maize) <br/>Disease: No disease<br/>

            <br/><br/> The crop is healthy!!!""",

        'Corn : Northern Leaf Blight': """ <b>Crop</b>: Corn <br/>Disease: Northern Leaf Blight
            <br/>
            <br/> Cause of disease:

            <br/><br/>Northern corn leaf blight (NCLB) is a foliar disease of corn (maize) caused by Exserohilum turcicum, the anamorph of the ascomycete Setosphaeria turcica. With its characteristic cigar-shaped lesions, this disease can cause significant yield loss in susceptible corn hybrids.

            <br/><br/> How to prevent/cure the disease <br/>
            <br/>1. Management of NCLB can be achieved primarily by using hybrids with resistance, but because resistance may not be complete or may fail, it is advantageous to utilize an integrated approach with different cropping practices and fungicides.

            <br/>2. Scouting fields and monitoring local conditions is vital to control this disease.""",

        'Grape : Black rot': """ <b>Crop</b>: Grape <br/>Disease: Black Rot<br/>
            <br/> Cause of disease:

            <br/><br/> 1. The black rot fungus overwinters in canes, tendrils, and leaves on the grape vine and on the ground. Mummified berries on the ground or those that are still clinging to the vines become the major infection source the following spring.

            <br/> 2. During rain, microscopic spores (ascospores) are shot out of numerous, black fruiting bodies (perithecia) and are carried by air currents to young, expanding leaves. In the presence of moisture, these spores germinate in 36 to 48 hours and eventually penetrate the leaves and fruit stems. 

            <br/> 3. The infection becomes visible after 8 to 25 days. When the weather is wet, spores can be released the entire spring and summer providing continuous infection.


            <br/><br/> How to prevent/cure the disease <br/>
            <br/>1. Space vines properly and choose a planting site where the vines will be exposed to full sun and good air circulation. Keep the vines off the ground and insure they are properly tied, limiting the amount of time the vines remain wet thus reducing infection.

            <br/>2. Keep the fruit planting and surrounding areas free of weeds and tall grass. This practice will promote lower relative humidity and rapid drying of vines and thereby limit fungal infection.

            <br/>3. Use protective fungicide sprays. Pesticides registered to protect the developing new growth include copper, captan, ferbam, mancozeb, maneb, triadimefon, and ziram. Important spraying times are as new shoots are 2 to 4 inches long, and again when they are 10 to 15 inches long, just before bloom, just after bloom, and when the fruit has set.""",

        'Grape : Black Measles': """ <b>Crop</b>: Grape <br/>Disease: Black Measles<br/>
            <br/> Cause of disease:

            <br/><br/> 1. Black Measles is caused by a complex of fungi that includes several species of Phaeoacremonium, primarily by P. aleophilum (currently known by the name of its sexual stage, Togninia minima), and by Phaeomoniella chlamydospora.

            <br/> 2. The overwintering structures that produce spores (perithecia or pycnidia, depending on the pathogen) are embedded in diseased woody parts of vines. The overwintering structures that produce spores (perithecia or pycnidia, depending on the pathogen) are embedded in diseased woody parts of vines.

            <br/> 3. During fall to spring rainfall, spores are released and wounds made by dormant pruning provide infection sites.

            <br/> 4. Wounds may remain susceptible to infection for several weeks after pruning with susceptibility declining over time.


            <br/><br/> How to prevent/cure the disease <br/>
            <br/>1. Post-infection practices (sanitation and vine surgery) for use in diseased, mature vineyards are not as effective and are far more costly than adopting preventative practices (delayed pruning, double pruning, and applications of pruning-wound protectants) in young vineyards. 


            <br/>2. Sanitation and vine surgery may help maintain yields. In spring, look for dead spurs or for stunted shoots. Later in summer, when there is a reduced chance of rainfall, practice good sanitation by cutting off these cankered portions of the vine beyond the canker, to where wood appears healthy. Then remove diseased, woody debris from the vineyard and destroy it.

            <br/>3. The fungicides labeled as pruning-wound protectants, consider using alternative materials, such as a wound sealant with 5 percent boric acid in acrylic paint (Tech-Gro B-Lock), which is effective against Eutypa dieback and Esca, or an essential oil (Safecoat VitiSeal).""",

        'Grape : Isariopsis Leaf Spot': """ <b>Crop</b>: Grape <br/>Disease: Isariopsis Leaf Spot<br/>
            <br/> Cause of disease:

            <br/><br/> 1. Grape Isariopsis Leaf Spot is caused by the fungus Isariopsis viticola, which thrives in warm, humid conditions.

            <br/> 2. It spreads through various means including rain splash, wind, or irrigation water, infecting leaves, shoots, and fruit.
            <br/><br/> How to prevent/cure the disease <br/>
            <br/>1. Vineyard Management: Proper vineyard management practices like pruning enhance air circulation, reducing humidity and minimizing favorable conditions for fungal growth.
            <br/>2. Fungicide Application: Timely application of fungicides containing active ingredients such as azoxystrobin or mancozeb can effectively prevent and manage Isariopsis Leaf Spot. Rotation of fungicides with different modes of action helps prevent resistance development in the fungal population.""",

        'Grape : Healthy': """ <b>Crop</b>: Grape <br/>Disease: No disease<br/>

            <br/><br/> The crop is healthy!!!""",

        'Potato : Early blight': """ <b>Crop</b>: Potato <br/>Disease: Early Blight<br/>
            <br/> Cause of disease:

            <br/><br/> 1. Early blight (EB) is a disease of potato caused by the fungus Alternaria solani. It is found wherever potatoes are grown. 

            <br/> 2. The disease primarily affects leaves and stems, but under favorable weather conditions, and if left uncontrolled, can result in considerable defoliation and enhance the chance for tuber infection. Premature defoliation may lead to considerable reduction in yield.

            <br/> 3. Primary infection is difficult to predict since EB is less dependent upon specific weather conditions than late blight.
            <br/><br/> How to prevent/cure the disease <br/>
            <br/>1. Plant only diseasefree, certified seed. 

            <br/>2. Follow a complete and regular foliar fungicide spray program.

            <br/>3. Practice good killing techniques to lessen tuber infections.
            <br/>4. Allow tubers to mature before digging, dig when vines are dry, not wet, and avoid excessive wounding of potatoes during harvesting and handling.""",

        'Potato : Late blight': """ <b>Crop</b>: Potato <br/>Disease: Late Blight<br/>

            Late blight is a potentially devastating disease of potato, infecting leaves, stems and fruits of plants. The disease spreads quickly in fields and can result in total crop failure if untreated. Late blight of potato was responsible for the Irish potato famine of the late 1840s.              
            <br/> Cause of disease:

            <br/><br/> 1. Late blight is caused by the oomycete Phytophthora infestans. Oomycetes are fungus-like organisms also called water molds, but they are not true fungi.

            <br/> 2. There are many different strains of P. infestans. These are called clonal lineages and designated by a number code (i.e. US-23). Many clonal lineages affect both tomato and potato, but some lineages are specific to one host or the other.
            <br/> 3. The host range is typically limited to potato and tomato, but hairy nightshade (Solanum physalifolium) is a closely related weed that can readily become infected and may contribute to disease spread. Under ideal conditions, such as a greenhouse, petunia also may become infected.


            <br/><br/> How to prevent/cure the disease <br/>
            <br/>1. Seed infection is unlikely on commercially prepared tomato seed or on saved seed that has been thoroughly dried.

            <br/>2. Inspect tomato transplants for late blight symptoms prior to purchase and/or planting, as tomato transplants shipped from southern regions may be infected

            <br/>3. If infection is found in only a few plants within a field, infected plants should be removed, disced-under, killed with herbicide or flame-killed to avoid spreading through the entire field.""",

        'Potato : Healthy': """ <b>Crop</b>: Potato <br/>Disease: No disease<br/>

            <br/><br/> The crop is healthy!!!""",

        'Tomato : Healthy': """ <b>Crop</b>: Tomato <br/>Disease: No disease<br/>

            <br/><br/> Don't worry. Your crop is healthy. Keep it up !!!""",

        'Tomato : Bacterial spot': """ <b>Crop</b>: Tomato <br/>Disease: Bacterial Spot<br/>
            <br/> Cause of disease:

            <br/><br/> 1. The disease is caused by four species of Xanthomonas (X. euvesicatoria, X. gardneri, X. perforans, and X. vesicatoria). In North Carolina, X. perforans is the predominant species associated with bacterial spot on tomato and X. euvesicatoria is the predominant species associated with the disease on pepper.

            <br/> 2. All four bacteria are strictly aerobic, gram-negative rods with a long whip-like flagellum (tail) that allows them to move in water, which allows them to invade wet plant tissue and cause infection.
            <br/><br/> How to prevent/cure the disease <br/>
            <br/>1. The most effective management strategy is the use of pathogen-free certified seeds and disease-free transplants to prevent the introduction of the pathogen into greenhouses and field production areas. Inspect plants very carefully and reject infected transplants- including your own!

            <br/>2. In transplant production greenhouses, minimize overwatering and handling of seedlings when they are wet.

            <br/>3. Trays, benches, tools, and greenhouse structures should be washed and sanitized between seedlings crops.
            <br/>4. Do not spray, tie, harvest, or handle wet plants as that can spread the disease""",

        'Tomato : Early blight': """ <b>Crop</b>: Tomato <br/>Disease: Early Blight<br/>
            <br/> Cause of disease:

            <br/><br/> 1. Early blight can be caused by two different closely related fungi, Alternaria tomatophila and Alternaria solani.
            <br/> 2. Alternaria tomatophila is more virulent on tomato than A. solani, so in regions where A. tomatophila is found, it is the primary cause of early blight on tomato. However, if A.tomatophila is absent, A.solani will cause early blight on tomato.
            <br/><br/> How to prevent/cure the disease <br/>
            <br/>1. Use pathogen-free seed, or collect seed only from disease-free plants..

            <br/>2. Rotate out of tomatoes and related crops for at least two years.

            <br/>3. Control susceptible weeds such as black nightshade and hairy nightshade, and volunteer tomato plants throughout the rotation.
            <br/>4. Fertilize properly to maintain vigorous plant growth. Particularly, do not over-fertilize with potassium and maintain adequate levels of both nitrogen and phosphorus.
            <br/>5. Avoid working in plants when they are wet from rain, irrigation, or dew.
            <br/>6. Use drip irrigation instead of overhead irrigation to keep foliage dry.""",

        'Tomato : Late blight': """ <b>Crop</b>: Tomato <br/>Disease: Late Blight<br/>

            Late blight is a potentially devastating disease of tomato, infecting leaves, stems and fruits of plants. The disease spreads quickly in fields and can result in total crop failure if untreated.              
            <br/> Cause of disease:

            <br/><br/> 1. Late blight is caused by the oomycete Phytophthora infestans. Oomycetes are fungus-like organisms also called water molds, but they are not true fungi.

            <br/> 2. There are many different strains of P. infestans. These are called clonal lineages and designated by a number code (i.e. US-23). Many clonal lineages affect both tomato and potato, but some lineages are specific to one host or the other.
            <br/> 3. The host range is typically limited to potato and tomato, but hairy nightshade (Solanum physalifolium) is a closely related weed that can readily become infected and may contribute to disease spread. Under ideal conditions, such as a greenhouse, petunia also may become infected.""",

        'Tomato : Leaf Mold': """ <b>Crop</b>: Tomato <br/>Disease: Leaf Mold<br/>
            <br/> Cause of disease:

            <br/><br/> 1. Leaf mold is caused by the fungus Passalora fulva (previously called Fulvia fulva or Cladosporium fulvum). It is not known to be pathogenic on any plant other than tomato.

            <br/> 2. Leaf spots grow together and turn brown. Leaves wither and die but often remain attached to the plant.
            <br/> 3. Fruit infections start as a smooth black irregular area on the stem end of the fruit. As the disease progresses, the infected area becomes sunken, dry and leathery.
            <br/><br/> How to prevent/cure the disease <br/>
            <br/>1. Use drip irrigation and avoid watering foliage.

            <br/>2. Space plants to provide good air movement between rows and individual plants.

            <br/>3. Stake, string or prune to increase airflow in and around the plant.
            <br/>4. Sterilize stakes, ties, trellises etc. with 10 percent household bleach or commercial sanitizer.
            <br/>5. Circulate air in greenhouses or tunnels with vents and fans and by rolling up high tunnel sides to reduce humidity around plants.
            <br/>6. Keep night temperatures in greenhouses higher than outside temperatures to avoid dew formation on the foliage.
            <br/>7. Remove crop residue at the end of the season. Burn it or bury it away from tomato production areas.""",

        'Tomato : Yellow leaf curl virus': """ <b>Crop</b>: Tomato <br/>Disease: Yellow Leaf Curl Virus<br/>
            <br/> Cause of disease:

            <br/><br/> 1. TYLCV is transmitted by the insect vector Bemisia tabaci in a persistent-circulative nonpropagative manner. The virus can be efficiently transmitted during the adult stages.

            <br/> 2. This virus transmission has a short acquisition access period of 15–20 minutes, and latent period of 8–24 hours.
            <br/><br/> How to prevent/cure the disease <br/>
            <br/>1. Currently, the most effective treatments used to control the spread of TYLCV are insecticides and resistant crop varieties.

            <br/>2. The effectiveness of insecticides is not optimal in tropical areas due to whitefly resistance against the insecticides; therefore, insecticides should be alternated or mixed to provide the most effective treatment against virus transmission.

            <br/>3. Other methods to control the spread of TYLCV include planting resistant/tolerant lines, crop rotation, and breeding for resistance of TYLCV. As with many other plant viruses, one of the most promising methods to control TYLCV is the production of transgenic tomato plants resistant to TYLCV."""

    }

    recommendation = mark_safe(disease_dic[diseases.disease])

    return render(request,'pestis_rec.html',{'disease':diseases,'recommendation':recommendation})


