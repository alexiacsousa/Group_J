# Group_J
Advanced Programming Project - Group J

Group members:  
    - Aléxia Sousa: 51894@novasbe.pt  
    - Giacomo Castiglioni: 73411@novasbe.pt  
    - Liane Kpocheme: 73516@novasbe.pt  
    - Simone Capata: 74777@novasbe.pt  

## Setup (Recommended)
To create the conda environment:
```
conda env create -f environment.yml
conda activate requirements_j
```

To update the conda environment:
```
conda env update -f environment.yml --prune
```


Run the Streamlit app:
```
streamlit run app/1_Environmental_Explorer.py
streamlit run app/pages/2_AI_Risk_Analysis.py
```
Run tests:
```
pytest -q
```
## 🌍 Impact on the UN Sustainable Development Goals (SDGs)

This project was designed with a clear vision: to democratize environmental monitoring by combining accessible satellite imagery with local, privacy-preserving Artificial Intelligence. By automating the detection of ecological threats, this application directly contributes to several of the **United Nations' Sustainable Development Goals (SDGs)**:

* **[Goal 15: Life on Land](https://sdgs.un.org/goals/goal15)** 🌳
  This is the primary focus of our application. By analyzing high-resolution ESRI satellite tiles, the AI can rapidly identify signs of deforestation, illegal logging, and land degradation. Providing an accessible tool to monitor forest cover changes empowers NGOs, local governments, and researchers to protect vital ecosystems and halt biodiversity loss without needing expensive cloud-computing infrastructure.

* **[Goal 13: Climate Action](https://sdgs.un.org/goals/goal13)** 🌡️
  Forests are our most crucial carbon sinks. By acting as an early warning system for environmental degradation, this tool helps communities respond faster to climate-related hazards (such as rapidly drying water bodies or expanding desertification), integrating vital data into climate change planning and mitigation strategies.

* **[Goal 11: Sustainable Cities and Communities](https://sdgs.un.org/goals/goal11)** 🏙️
  The application isn't just for wild areas; it can also analyze urban environments. By inputting city coordinates, the AI can assess the balance between concrete infrastructure and green spaces, helping urban planners recognize the environmental risks of uncontrolled expansion and work toward more inclusive and sustainable urbanization.

Ultimately, by relying on local AI models (`moondream` and `llama3.2:1b`), this project ensures that environmental protection tools are sustainable, low-cost, and accessible even to communities with limited internet bandwidth, bridging the technological divide in ecological preservation.

---

## 🚨 AI Risk Identification Showcase

Below are three real-world examples demonstrating the application's ability to analyze coordinates, describe the landscape, and successfully flag environmental dangers.

### Example 1: Active Deforestation (Amazon Rainforest)
* **Coordinates:** Lat -9.36, Lon -63.00 (Zoom 15)
* **Risk Level:** 🔴 High

 
**AI Vision Description:** The image presents an aerial view of a densely forested area. The predominant color scheme is green, indicating the presence of vegetation such as trees and bushes covering most of the landscape. There are also some visible water bodies in the vicinity, suggesting that this region might be near a river or lake. Additionally, there are roads and buildings scattered throughout the scene, which could potentially indicate human activity in the area. The image also contains signs of deforestation, erosion, flooding, pollution, or land degradation, indicating possible environmental concerns related to the management and preservation of this lush green landscape.

**AI Risk Assessment:** 
Main Risks: Forests: Deforestation, Monoculture Risk; Rivers/Lakes: Water Pollution

Explanation: The dense forested area is highly vulnerable due to recent significant deforestation (2020) exceeding annual targets and high rates of forest clearance. This could exacerbate monoculture practices, leading to further habitat loss for local biodiversity. Additionally, the surrounding waters could be affected by increased pollution from agricultural runoff and industrial activities, posing a risk to aquatic life and human health.

### Example 2: Urban Environment & Coastal Monitoring (Lisbon, Portugal)
* **Coordinates:** Lat 38.72, Lon -9.14 (Zoom 15)
* **Risk Level:** 🟡 Medium 


 **AI Vision Description:** The satellite image shows an aerial view of a densely populated city with numerous buildings in shades of orange and brown. The city is surrounded by water bodies, indicating its proximity to the sea or river. The vegetation appears sparse, suggesting that some areas might be experiencing deforestation or land degradation. There are roads crisscrossing through the city, connecting different parts of the urban landscape. The image also contains signs of pollution, such as industrial or mining areas and possibly a factory in the vicinity. Overall, the scene highlights the complex relationship between human activity and the environment within this densely populated urban setting.
 
 **AI Risk Assessment:** 
Main Risks: Forest degradation, Urban sprawl

Explanation: The satellite image suggests that the city is experiencing significant deforestation due to urbanization and human activities, such as construction and industrial development. The sparse vegetation in some areas could indicate degraded land, which is a sign of long-term environmental stress. Additionally, the presence of pollution signs around the city implies a lack of effective waste management and environmental regulations, contributing to environmental degradation. These factors highlight the complex interplay between human activity and environmental concerns within this densely populated urban setting.

### Example 3: Severe Land Degradation (Bingham Canyon Mine, USA)
* **Coordinates:** Lat 40,52, Lon -112,15 (Zoom 15)
* **Risk Level:** 🟡 Medium 



**AI Vision Description:** The satellite image shows an aerial view of a large open area that appears to be a coal mine or industrial site. The landscape features numerous hills and valleys, indicating the presence of mountains in the background. The terrain is predominantly covered in dirt and bare soil, with some vegetation scattered throughout. There are also several roads and buildings within the scene, suggesting human activity and infrastructure development around the area.

The image highlights potential environmental concerns such as deforestation, flooding, erosion, or pollution resulting from industrial activities. These issues can have a significant impact on the surrounding ecosystem and may require careful planning and management to minimize their effects on the environment and local communities.


**AI Risk Assessment:**
Main Risks: Deforestation, Urban sprawl, Soil degradation

Explanation: The satellite image suggests that the area is likely to be a coal mine or industrial site, which poses significant environmental threats due to deforestation and soil degradation. As a coal mine, it may also lead to air and water pollution, while its proximity to human activity and infrastructure development increases the risk of urban sprawl and associated problems such as heat islands and increased greenhouse gas emissions. The image does not provide clear evidence of flooding or erosion, but these issues are also possible due to the industrial activities around the site. Overall, the potential environmental impacts on the surrounding ecosystem and local communities require careful planning and management to minimize their effects.