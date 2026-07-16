
# SisFall: A Fall and Movement Dataset

Research on fall and movement detection with wearable devices has witnessed promising growth.

29 minutos de lectura

Ver original

---

## Abstract

Research on fall and movement detection with wearable devices has witnessed promising growth. However, there are few publicly available datasets, all recorded with smartphones, which are insufficient for testing new proposals due to their absence of objective population, lack of performed activities, and limited information. Here, we present a dataset of falls and activities of daily living (ADLs) acquired with a self-developed device composed of two types of accelerometer and one gyroscope. It consists of 19 ADLs and 15 fall types performed by 23 young adults, 15 ADL types performed by 14 healthy and independent participants over 62 years old, and data from one participant of 60 years old that performed all ADLs and falls. These activities were selected based on a survey and a literature analysis. We test the dataset with widely used feature extraction and a simple to implement threshold based classification, achieving up to 96% of accuracy in fall detection. An individual activity analysis demonstrates that most errors coincide in a few number of activities where new approaches could be focused. Finally, validation tests with elderly people significantly reduced the fall detection performance of the tested features. This validates findings of other authors and encourages developing new strategies with this new dataset as the benchmark.

**Keywords:** triaxial accelerometer, wearable devices, fall detection, mobile health-care, SisFall

## 1. Introduction

The number of elderly people living alone has been continuously growing worldwide. This independence comes with the risk of not receiving prompt attention if an accident occurs. A third of the people over 65 years old suffer on average one fall per year [[1](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#B1-sensors-17-00198)], and this number grows with age [[2](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#B2-sensors-17-00198)] and previous falls, where about one third develop fear of falling again [[3](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#B3-sensors-17-00198),[4](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#B4-sensors-17-00198)]. Not receiving attention in the first hour of the accident increases the risk of death and chronic affections [[5](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#B5-sensors-17-00198)]. This issue has been widely addressed in recent years with systems that detect falls in elderly people, and generate a prompt alert that can reduce the consequences related to medical attention response time [[6](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#B6-sensors-17-00198)]. These systems have acceptance among the objective population as a way to support their independence and reduce their fear of falling [[7](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#B7-sensors-17-00198)].

Developers of fall detection systems are currently facing several challenges. Independently of the acquisition strategy, most works are not tested with the objective population (elderly people), reducing their accuracy in real-life applications [[8](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#B8-sensors-17-00198)]. Moreover, all public datasets exclusively contain data from young adults, making it difficult to test new proposals [[9](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#B9-sensors-17-00198)]. Here, we make publicly available a dataset with falls and activities of daily living (ADLs) acquired with a wearable device, and we provide results of some of the most commonly used detection features with both young and elderly people. The purpose of this work is to provide a benchmark for other researchers on the fall and movement detection field, and to address two rarely discussed open issues: training with young people features intended for elderly people, and setting-up algorithms for maximum accuracy instead of maximum sensitivity.

Falls are commonly detected with wearable or ambient-based systems (see [[6](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#B6-sensors-17-00198),[9](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#B9-sensors-17-00198),[10](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#B10-sensors-17-00198),[11](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#B11-sensors-17-00198),[12](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#B12-sensors-17-00198)] for reviews in the field). Ambient-based sensors such as cameras are intrusive and do not solve the problem for independent adults, who are not confined to closed spaces. According to [[2](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#B2-sensors-17-00198)], up to 50% of the falls in independent elderly people occur outside the home premises. Wearable devices offer portability as they can be used regardless of the user location. Available wearable devices include smartphone apps and self-developed systems. In both cases, the preferred sensor is the triaxial accelerometer because of its low cost, small size, and because it is built-in in almost all smartphones [[6](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#B6-sensors-17-00198)]. Smartphones are a popular selection for authors because they include a robust hardware, a powerful processor, and they are economically affordable [[6](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#B6-sensors-17-00198),[11](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#B11-sensors-17-00198)]. However, the low cost of the individual components and design tools has encouraged authors to develop their own embedded devices too [[13](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#B13-sensors-17-00198)].

Independently of the device used, authors have faced problems such as energy consumption, battery life, false positives (the alarm turns on with ADL), false negatives (the alarm does not turn on with falls), and user comfort issues. Specifically for smartphones, these devices are not designed for constant use of the processor and sensors (the battery goes off in a couple of hours [[11](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#B11-sensors-17-00198)]). Additionally, the smartphone may get hits and falls caused by manipulation, or the person may forget it in a table after calling, making it less feasible for permanent monitoring.

New strategies for solving the aforementioned problems require testing. It requires acquiring datasets with common types of falls and ADLs. In this sense, some authors analyzed how elderly people fall. Back in 1993, authors in [[5](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#B5-sensors-17-00198)] performed a wide survey with 704 women over 65 years old. They reported that most falls were caused by trips, slips and loss of balance. However, they did not record data. About the conditions of the fall, in [[14](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#B14-sensors-17-00198)], the authors found that women were three times more likely to hit the ground on the hips than men, and that most people fell in a forward direction with 60% of prevalence. Most activities currently selected for testing algorithms are based on these studies.

Once the selected ADL and falls are simulated and recorded, the raw acceleration data must be processed and classified. Authors commonly filter the data, apply a feature extraction, and classify activities as falls or ADL. The literature provides a wide number of features (see [[9](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#B9-sensors-17-00198)], Table 4 and [[12](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#B12-sensors-17-00198)], Table 2 for complete lists). Unfortunately, there are not works in the literature tested with independent elderly people (see [[9](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#B9-sensors-17-00198)], Table 1, and [[12](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#B12-sensors-17-00198)], Table 4) and available public datasets were all recorded exclusively with young adults. In [[8](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#B8-sensors-17-00198)], for example, authors tested 13 state-of-the-art approaches with real elderly people falls, and they found that the performance of these approaches severely decreased under real-life conditions. However, they did not release the validation dataset, i.e., other authors cannot analyze why those features reduced their performance, and, more importantly, how to solve it. To our knowledge, there only exist four public datasets, all acquired using smartphones: Mobifall [[15](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#B15-sensors-17-00198)], tFall [[16](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#B16-sensors-17-00198)], DLR [[17](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#B17-sensors-17-00198)], and project gravity [[18](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#B18-sensors-17-00198)]. Igual et al. [[19](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#B19-sensors-17-00198)] compared the former three and found severe variability and performance issues of the analyzed algorithms.

In this paper, we present and make publicly available a complete dataset of falls and ADL acquired with a self-developed embedded device that can be easily replicated (see [[20](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#B20-sensors-17-00198),[21](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#B21-sensors-17-00198)] for example designs). It includes young adults and elderly people performing a wide variety of activities selected from a survey and previous studies. The dataset contains 19 types of ADLs and 15 types of falls. It includes acceleration (from two accelerometers) and rotation (from a gyroscope) data from 38 volunteers divided into two groups: 23 adults between 19 and 30 years old, and 15 elderly people between 60 and 75 years old. The dataset is available for free download as [Supplementary Materials](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#app1-sensors-17-00198) [[22](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#B22-sensors-17-00198)], and videos of each type of activity within the dataset are also included for helping the reader to replicate this work. Additionally, a comparative analysis between several features used in the literature is presented as a reference for future works.

## 2. Related Public Datasets

Our search on public datasets of falls and ADLs was focused on wearable devices, as ambient based and video fall detection systems are too restrictive to help independent elderly people (the objective population of this work). We also considered some basic requirements for a dataset to be useful: all activities must be well documented, the raw data must be freely available, the dataset must contain both falls and ADLs ([[23](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#B23-sensors-17-00198)], for example, examining several public datasets, but none including falls), and it must be reported in a peer-reviewed paper. Following these premises, we found four datasets:

- MobiFall [[15](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#B15-sensors-17-00198)]: twenty-four volunteers (22 to 42 years old) performed nine types of ADLs and four of falls using a Samsung Galaxy smartphone, Samsung, Seoul, South Korea. Nine subjects performed falls and ADLs, while 15 performed only falls (three trials each).
    
- tFall [[16](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#B16-sensors-17-00198)]: ten participants between 20 and 42 years old. They recorded eight types of falls (503 total recordings with two smartphones), and one week of continuous ADL recordings with all participants carrying smartphones in the pockets and a handbag. The ADL trials were not identified by activity.
    
- DLR [[17](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#B17-sensors-17-00198)]: sixteen subjects (23 to 50 years old). They recorded six types of ADLs, and the authors did not specify the conditions of the falls (they belong to a single group). The files are too short for some types of analysis.
    
- Project gravity [[18](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#B18-sensors-17-00198)]: three participants (ages 22, 26, and 32) performed 12 types of falls and seven types of ADLs with a smartphone in the pocket.
    

None of these datasets includes elderly people, and their variety of activities and number of subjects is limited compared to this work. Additionally, all authors used smartphones in the pocket for recordings. Here, we fixed our device as a belt buckle as recommended in previous works [[24](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#B24-sensors-17-00198),[25](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#B25-sensors-17-00198)].

## 3. Materials and Methods

### 3.1. Selection of Activities

Additionally to those falls and ADLs commonly tested in the literature (see [[9](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#B9-sensors-17-00198)], Table 4), we performed a survey with elderly people living alone and administrative personnel from retirement homes. The survey consisted of three main questions: For each fall incident, (_i_) which activity were you performing when the fall happened? (_ii_) What produced the fall? A sliding, a faint, a trip, other? (_iii_) In which orientation did the fall happen? What part of the body received the impact?. The survey was conducted with 15 elderly people from the psycho-physic program of the Universidad de Antioquia (between July and August 2014, in Medellín, Colombia), and 17 retirement homes (between October 2014 and January 2015, in Medellín and Manizales, Colombia).

As a result of the survey, the independent elderly people fall more when walking, taking a shower, and walking up or down stairs; and fall less when trying to get up or sit down in a chair or a bed, or bending. On the other hand, elderly people living in retirement homes fall more when walking and when trying to get up from a chair or a bed and fall less when walking up or down stairs. The answers given by the participants were consistent with the results presented in [[5](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#B5-sensors-17-00198)]. [Table 1](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#sensors-17-00198-t001) shows the types of falls selected for this work. Falling when walking up or down stairs was identified as a common type of fall in the survey, but it was not included here because of the high risk of having an accident.

#### Table 1.

Types of falls selected for this work.

|Code|Activity|Trials|Duration|
|---|---|---|---|
|F01|Fall forward while walking caused by a slip|5|15 s|
|F02|Fall backward while walking caused by a slip|5|15 s|
|F03|Lateral fall while walking caused by a slip|5|15 s|
|F04|Fall forward while walking caused by a trip|5|15 s|
|F05|Fall forward while jogging caused by a trip|5|15 s|
|F06|Vertical fall while walking caused by fainting|5|15 s|
|F07|Fall while walking, with use of hands in a table to dampen fall, caused by fainting|5|15 s|
|F08|Fall forward when trying to get up|5|15 s|
|F09|Lateral fall when trying to get up|5|15 s|
|F10|Fall forward when trying to sit down|5|15 s|
|F11|Fall backward when trying to sit down|5|15 s|
|F12|Lateral fall when trying to sit down|5|15 s|
|F13|Fall forward while sitting, caused by fainting or falling asleep|5|15 s|
|F14|Fall backward while sitting, caused by fainting or falling asleep|5|15 s|
|F15|Lateral fall while sitting, caused by fainting or falling asleep|5|15 s|

ADLs of [Table 2](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#sensors-17-00198-t002) were selected based on: common activities, activities that are similar (in acceleration waveform) to falls, and activities with high acceleration that can generate false positives. All ADL and falls selected for this work were approved by a physician specialized in sports. The [Supplementary Materials](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#app1-sensors-17-00198) contains videos of each type of fall and ADL performed by the participants, as an effort to solve another drawback in the literature: showing the exact conditions of the recordings [[22](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#B22-sensors-17-00198)].

#### Table 2.

Types of activities of daily living selected for this work.

|Code|Activity|Trials|Duration|
|---|---|---|---|
|D01|Walking slowly|1|100 s|
|D02|Walking quickly|1|100 s|
|D03|Jogging slowly|1|100 s|
|D04|Jogging quickly|1|100 s|
|D05|Walking upstairs and downstairs slowly|5|25 s|
|D06|Walking upstairs and downstairs quickly|5|25 s|
|D07|Slowly sit in a half height chair, wait a moment, and up slowly|5|12 s|
|D08|Quickly sit in a half height chair, wait a moment, and up quickly|5|12 s|
|D09|Slowly sit in a low height chair, wait a moment, and up slowly|5|12 s|
|D10|Quickly sit in a low height chair, wait a moment, and up quickly|5|12 s|
|D11|Sitting a moment, trying to get up, and collapse into a chair|5|12 s|
|D12|Sitting a moment, lying slowly, wait a moment, and sit again|5|12 s|
|D13|Sitting a moment, lying quickly, wait a moment, and sit again|5|12 s|
|D14|Being on one’s back change to lateral position, wait a moment, and change to one’s back|5|12 s|
|D15|Standing, slowly bending at knees, and getting up|5|12 s|
|D16|Standing, slowly bending without bending knees, and getting up|5|12 s|
|D17|Standing, get into a car, remain seated and get out of the car|5|25 s|
|D18|Stumble while walking|5|12 s|
|D19|Gently jump without falling (trying to reach a high object)|5|12 s|

### 3.2. Participants

This database was generated with collaboration of 38 volunteers divided into two groups: elderly people and young adults. Elderly people group was formed by 15 participants (8 male and 7 female), and the young adults group was formed by 23 participants (11 male and 12 female). [Table 3](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#sensors-17-00198-t003) shows age, weight, and height of each group. Individual information is available in the readme [[22](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#B22-sensors-17-00198)]. The elderly people group is formed by retired employees of the Universidad de Antioquia and parents of current employees. They all were healthy and independent, and none of them presented gait problems.

#### Table 3.

Age, height and weight of the participants.

||Sex|Age|Height (m)|Weight (kg)|
|---|---|---|---|---|
|Elderly|Female|62–75|1.50–1.69|50–72|
|Male|60–71|1.63–1.71|56–102|
|Adult|Female|19–30|1.49–1.69|42–63|
|Male|19–30|1.65–1.83|58–81|

Young adults performed ADLs and falls. Elderly people did not perform falls and activities D06, D13, D18, and D19 from [Table 2](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#sensors-17-00198-t002) due to recommendations of the physician specialized in sports. Additionally, some elderly people did not perform some activities due to personal impairments (or medical recommendation). The participant of 60 years old identified by code SE06, who is an expert in Judo simulated both falls and ADLs.

All subjects gave their informed consent for inclusion before they participated in the study. The study was conducted in accordance with the Declaration of Helsinki, and the protocol was approved by the Bio-Ethics Committee of the Medicine Faculty, Universidad de Antioquia UDEA (Medellín, Colombia). Additionally, all participants were evaluated by a physician specialized in sports.

### 3.3. Experimental Set-Up

The dataset was recorded with a self-developed embedded device composed of a Kinets MKL25Z128VLK4 microcontroller (NPX, Austin, Texas, USA), an Analog Devices (Norwood, Massachusetts, USA) ADXL345 accelerometer (configured for ±16 g, 13 bits of analog to digital converter –ADC), a Freescale MMA8451Q accelerometer (±8 g, 14 bits of ADC), an ITG3200 gyroscope (±2000∘/s, 16 bits of ADC. Texas Instruments, Dallas, Texas, USA), an SD card for recording, and a 1000 mA/h generic battery. The device was fixed to the waist of the participants ([Figure 1](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#sensors-17-00198-f001)). This location provides high distinction among activities for a single accelerometer system [[24](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#B24-sensors-17-00198),[25](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#B25-sensors-17-00198)].

#### Figure 1.

[![Figure 1](https://cdn.ncbi.nlm.nih.gov/pmc/blobs/a489/5298771/27f84289ab94/sensors-17-00198-g001.jpg)](https://www.ncbi.nlm.nih.gov/core/lw/2.0/html/tileshop_pmc/tileshop_pmc_inline.html?title=Click%20on%20image%20to%20zoom&p=PMC3&id=5298771_sensors-17-00198-g001.jpg)

Device used for acquisition. The self-developed embedded device included two accelerometers and a gyroscope. It was fixed to the waist of the participants.

Only acceleration data acquired with the ADXL345 sensor was used in this work, as it is energy efficient and provides the larger span. However, the data recorded with the other accelerometer and the gyroscope are also publicly available for further studies. The orientation of the sensor (see [Figure 1](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#sensors-17-00198-f001)) presents the positive _z_-axis in the forward direction, the positive _y_-axis in the gravity direction, and the positive _x_-axis pointing to the right side of the participant. All tests were performed with the original frequency sample of 200 Hz.

The classrooms and open spaces of a coliseum at the Universidad de Antioquia (Medellín, Colombia) were used for recording the activities. In order to guarantee safety conditions, falls were simulated using safety landing mats. Activity D17 from [Table 2](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#sensors-17-00198-t002) was recorded using the copilot chair of a Renault Logan car. The time required for recording all trials was approx. 1.5 h for each elderly person and 3.5 h for each young adult.

### 3.4. Fall Detection Algorithms

Here, we test commonly known features as a way to provide a preliminary analysis with the proposed dataset. We follow the common pipeline to process the data: preprocessing, feature extraction, classification, and validation.

#### 3.4.1. Preprocessing Stage

Preprocessing is critical in the performance of the classification algorithms and their computational burden. In this work, we performed a comparison between using preprocessing or not in fall detection. The preprocessing stage consisted of a 4th order IIR Butterworth low-pass filter with cut-off frequency of 5 Hz. This filter was selected due to its simplicity, as it presented similar results than more elaborated IIR and FIR filters (including different cut-off frequencies) that we analyzed in preliminary tests.

#### 3.4.2. Feature Extraction

The objective of this stage is to maximize the separation between ADL and falls. We tested several commonly used features listed in ([[9](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#B9-sensors-17-00198)], Table 4 and [[12](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#B12-sensors-17-00198)], Table 2) (original implementation details can be followed in the references therein). We separated the features in five groups: amplitude, orientation angle, statistical moments, critical phase time, and area under the curve. [Table 4](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#sensors-17-00198-t004) includes those features that presented the best overall performance.

##### Table 4.

Feature extraction characteristics used to test the proposed dataset.

|Type|Code|Feature|Equation|
|---|---|---|---|
|Amplitude|𝐶1|Sum vector magnitude|𝐶1⁡[𝑘]=𝑅⁢𝑀⁢𝑆⁡(˜𝑎⁡[𝑘])=√𝑎2𝑥⁡[𝑘]+𝑎2𝑦⁡[𝑘]+𝑎2𝑧⁡[𝑘]|
|𝐶2|Sum vector magnitude on horizontal plane|𝐶2⁡[𝑘]=√𝑎2𝑥⁡[𝑘]+𝑎2𝑧⁡[𝑘]|
|𝐶3|Maximum peak-to-peak acceleration amplitude|𝐶3⁡[𝑘]=𝑅⁢𝑀⁢𝑆⁢(max⁡(˜𝑎⁡[𝑘])−min⁡(˜𝑎⁡[𝑘]))|
|Orientation|𝐶4|Angle between _z_-axis and vertical|𝐶4⁡[𝑘]=atan⁢2⁢(√(˜𝑎𝑥⁡[𝑘])2+(˜𝑎𝑧⁡[𝑘])2,−˜𝑎𝑦⁡[𝑘])|
|𝐶5|Orientation of person’s trunk|𝐶5⁡[𝑘]=𝜎⁡(atan⁡(𝑅⁢𝑀⁢𝑆⁡(˜𝑎𝑥⁡[𝑘],˜𝑎𝑧⁡[𝑘])˜𝑎𝑦⁡[𝑘]))|
|𝐶6|Orientation change in horizontal plane|𝐶6⁡[𝑘]=mean⁡(→𝑎𝑥⁡[𝑘−𝑁])·mean⁡(→𝑎𝑥⁡[𝑘])|
|Time|𝐶7|Jerk (rate of acceleration change)|𝐶7⁡[𝑘]=→𝑎𝑥⁡[𝑘]−→𝑎𝑥⁡[𝑘−𝑁]𝑡⁡[𝑘]−𝑡⁡[𝑘−𝑁]|
|Statistics|𝐶8|Standard deviation magnitude on horizontal plane|𝐶8⁡[𝑘]=√𝜎2𝑥⁡[𝑘]+𝜎2𝑧⁡[𝑘]; with 𝜎𝑖=std⁡(˜𝑎𝑖⁡[𝑘])|
|𝐶9|Standard deviation magnitude|𝐶9⁡[𝑘]=√𝜎2𝑥⁡[𝑘]+𝜎2𝑦⁡[𝑘]+𝜎2𝑧⁡[𝑘]|
|Area|𝐶10|Signal magnitude area|𝐶10⁡[𝑘]=1𝑁⁢(∫\|⁢˜𝑎𝑥⁢[𝑘]⁢\|𝑑⁢𝑡+∫\|⁢˜𝑎𝑦⁢[𝑘]⁢\|𝑑⁢𝑡+∫\|⁢˜𝑎𝑧⁢[𝑘]\|𝑑⁢𝑡)|
|𝐶11|Signal magnitude area on horizontal plane|𝐶11⁡[𝑘]=1𝑁⁢(∫\|⁢˜𝑎𝑥⁢[𝑘]⁢\|𝑑⁢𝑡+∫\|⁢˜𝑎𝑧⁢[𝑘]\|𝑑⁢𝑡)|
|𝐶12|Activity signal magnitude area|𝐶12⁡[𝑘]=∫(√˜𝑎2𝑥⁡[𝑛]+˜𝑎2𝑦⁡[𝑛]+˜𝑎2𝑧⁡[𝑛])𝑑𝑛|
|𝐶13|Activity signal magnitude area on horizontal plane|𝐶13⁡[𝑘]=∫(√˜𝑎2𝑥⁡[𝑛]+˜𝑎2𝑧⁡[𝑛])𝑑𝑛|
|𝐶14|Velocity (approx.)|𝐶14⁡[𝑘]=1𝑁⁢√(∫˜𝑎𝑥⁡[𝑘]𝑑𝑡)2+(∫˜𝑎𝑧⁡[𝑘]𝑑𝑡)2|

Here, one sample of acceleration in the three axis is defined as the vector →𝑎=[𝑎𝑥,𝑎𝑦,𝑎𝑧]𝑇∈ℜ3, the sliding window used for computing the dynamic features is denoted with ˜𝑎⁡[𝑘]=[→𝑎𝑇⁡[𝑘−𝑁𝑣+1],⋯,→𝑎𝑇⁡[𝑘]]𝑇∈ℜ𝑁𝑣×3, at time sample _k_, where 𝑁𝑣 is the number of samples in the selected window. The standard deviation operator is defined as 𝜎⁡(·), and RMS refers to the Root Mean Square value. The integrals were computed with the trapezoid method, with limits 𝑘−𝑁𝑣+1 to _k_.

#### 3.4.3. Classification

A simple to implement threshold-based classifier was selected for this work. Threshold-based classification is still the most widely used strategy for fall detection, as it is less computationally intensive than support vector machines and similar classification algorithms [[11](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#B11-sensors-17-00198)]. We analyzed two widely used alternatives: Threshold 1 (𝑇1) which follows maximum accuracy, and Threshold 2 (𝑇2) which maximizes the sensitivity (fall detection capability). The sensitivity (SE), specificity (SP) and accuracy (AC) were computed as follows [[26](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#B26-sensors-17-00198)]:

|   |   |
|---|---|
|SE=𝑇⁢𝑃𝑇⁢𝑃+𝐹⁡𝑁SP=𝑇⁢𝑁𝑇⁢𝑁+𝐹⁡𝑃AC=SE+SP2,|(1)|

where 𝑇⁢𝑃 and 𝑇⁢𝑁 are the true positives and negatives; 𝐹⁡𝑃 and 𝐹⁡𝑁 the false positives and negatives, respectively. The way we computed the accuracy allows using an unbalanced number of ADLs and fall trials in a single test. Validation data was tested with the chosen thresholds following a 10-fold cross-validation.

[Figure 2](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#sensors-17-00198-f002) shows an example of the preprocessing stage and the computation of feature 𝐶8 for ADL D11 (trying to get-up from a chair and fail—[Figure 2](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#sensors-17-00198-f002)a) and fall F05 (trip and fall while jogging—[Figure 2](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#sensors-17-00198-f002)b), with threshold 𝑇1. This ADL was selected because of its high peak acceleration. Despite this, 𝐶8 peak was around 40% below the threshold value ([Figure 2](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#sensors-17-00198-f002)a—bottom). On the other hand, feature 𝐶8 far crossed the threshold during fall F05 ([Figure 2](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#sensors-17-00198-f002)b—bottom). Note that while jogging before the fall, which is a high acceleration activity, feature 𝐶8 was always below the threshold.

##### Figure 2.

[![Figure 2](https://cdn.ncbi.nlm.nih.gov/pmc/blobs/a489/5298771/c9a7e1d806ee/sensors-17-00198-g002.jpg)](https://www.ncbi.nlm.nih.gov/core/lw/2.0/html/tileshop_pmc/tileshop_pmc_inline.html?title=Click%20on%20image%20to%20zoom&p=PMC3&id=5298771_sensors-17-00198-g002.jpg)

Example of processing and classification. The features are computed after the filtering process of the raw data. (**a**) ADL D11 gives 𝐶8 values below threshold 𝑇1 (horizontal **red** line); (**b**) Feature 𝐶8 crosses the threshold when the fall in activity F05 is detected.

#### 3.4.4. Cross-Validation

The robustness of the classification stage was analyzed with a 10-fold cross-validation set-up. All analysis were performed guaranteeing the same proportion of falls and ADLs in the groups. Each group was used in one fold as validation data.

In the following section, we analyze three commonly discussed issues: the effect of preprocessing, the importance of including elderly people in the training stage, and the way the threshold is selected. We finish this study with a novel activity-by-activity analysis that demonstrates how most errors occur in specific activities.

## 4. Results

### 4.1. Effect of Filtering as the Preprocessing Stage

We initially tested the effect of filtering before applying the features of [Table 4](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#sensors-17-00198-t004). We used data from all 38 subjects for this analysis (4510 trials). [Figure 3](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#sensors-17-00198-f003) shows the mean accuracy obtained in validation with each feature after a 10-fold cross-validation for both raw and filtered data. Dynamic features were computed within sliding-horizon windows with full overlap. The window size (𝑁𝑣) for each feature was selected based on a heuristic analysis with windows between 200 ms and 2 s. Most dynamic features are commonly associated with the prior to the fall phase, or with the critical phase of the fall, which are estimated between 300–500 ms [[27](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#B27-sensors-17-00198)]. However, in this work, only 𝐶10, 𝐶11, and 𝐶14 performed better with a window of 𝑁𝑣=500 ms. The other dynamic features improved with 𝑁𝑣=1 s (200 samples).

#### Figure 3.

[![Figure 3](https://cdn.ncbi.nlm.nih.gov/pmc/blobs/a489/5298771/ad220b9c9b43/sensors-17-00198-g003.jpg)](https://www.ncbi.nlm.nih.gov/core/lw/2.0/html/tileshop_pmc/tileshop_pmc_inline.html?title=Click%20on%20image%20to%20zoom&p=PMC3&id=5298771_sensors-17-00198-g003.jpg)

Accuracy obtained in validation after a 10-fold cross-validation without (raw data) and with preprocessing (filtered). Features 𝐶2 and 𝐶8 achieved 95.0% and 96.1% of accuracy when the filter was applied, respectively. However, not all features improved their performance after filtering.

From [Figure 3](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#sensors-17-00198-f003), features 𝐶2 and 𝐶8 obtained the higher accuracy once the filter was applied (95.0%±1.2% and 96.1%±0.75%, respectively). This result is consistent with the literature ([[9](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#B9-sensors-17-00198)], Table 1). In this case, 𝐶2 would be preferred as it is static, i.e., it requires less memory and computational effort to be computed. The main difference between 𝐶2 and the well known sum vector magnitude (𝐶1) is that it only includes the horizontal plane (_x_-axis and _z_-axis in our device). The position of the sensor in the center of mass of the body allows neglecting the vertical axis from the computation. With this, we reduce the number of false positives caused by the high accelerations achieved in the _y_-axis with many ADLs (walk, run, jump, etc.).

Regarding the other features, it is evident that not all of them improved their performance after filtering. Specifically, those based on integration behaved better without preprocessing, which is expected as they may reduce high frequency noise as a low-pass filter. Feature 𝐶13, for example, achieved similar accuracy to 𝐶2 without the need of implementing a digital filter. Selecting the best fitted feature would depend on the embedded device used and the way they are implemented. Finally, orientation and time based features presented an overall poor performance (comparable to the sum vector magnitude).

The inclusion of the filtering stage also defines the minimum allowed frequency sample. A preliminary analysis indicated that more elaborated filters or higher cut frequency values did not improve the accuracy. This result is meaningful as it suggests that a frequency sample of up to 11 Hz could be enough for fall detection (lower than any work in the literature), with its respective burden reduction. This gives an advantage to those features that performed better with the filter, given that the frequency sample is critical in wearable devices. This is because (_i_) the system remains more time in idle state; and (_ii_) more separation among samples allows more computations of the classifier. SisFall dataset was released with its original 200 Hz frequency sample, as a way to encourage other authors to obtain their own conclusions.

For illustrative purposes, in the remainder of this paper, we only show results of the five features that best performed: 𝐶2, 𝐶3, 𝐶8, 𝐶9, and 𝐶13.

### 4.2. Training with Young vs. Elderly People

Our second proof-of-principle experiment accounted if training fall detection algorithms with young adults is adequate to use with elderly people. [Table 5](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#sensors-17-00198-t005) shows sensitivity (SE), specificity (SP) and accuracy (AC) results after a 10-fold cross-validation performed only with data from young adults, and the results of using the obtained 𝑇1 thresholds (included in [Table 6](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#sensors-17-00198-t006)) to test with data from elderly people.

#### Table 5.

Sensitivity (SE), specificity (SP) and accuracy (AC) after training with young adults and validating either with young adults or elderly people.

|Feature|Young|   |   |Elderly|   |   |
|---|---|---|---|---|---|---|
|SE|SP|AC|SE|SP|AC|
|---|---|---|---|---|---|
|𝐶2|**94.28**|96.13|95.21|**77.33**|97.67|87.49|
|𝐶3|**98.53**|80.50|89.51|**84.00**|96.42|90.21|
|𝐶8|**95.54**|96.38|95.96|**85.33**|98.10|91.72|
|𝐶9|**97.79**|80.70|89.25|**88.00**|96.42|92.21|
|𝐶13|**92.56**|94.41|93.49|**62.67**|95.19|78.93|

#### Table 6.

Variation in accuracy and threshold 𝑇1 after training exclusively with the young but validating with elderly people (test 1), and then training and validating with elderly people (test 2).

|Feature|AC (%) with Elderly|   |Threshold 𝑻𝟏|   |
|---|---|---|---|---|
|Test 1|Test 2|Test 1|Test 2|
|---|---|---|---|
|𝐶2|87.49|90.45 ± 5.89|1.07 ± 0.029|0.97 ± 0.012|
|𝐶3|90.21|90.85 ± 7.25|1.48 ± 0.017|1.23 ± 0.024|
|𝐶8|91.72|92.36 ± 6.80|0.40 ± 0.004|0.36 ± 0.003|
|𝐶9|92.21|92.58 ± 7.10|0.43 ± 0.009|0.36 ± 0.002|
|𝐶13|78.93|80.73 ± 5.62|0.08 ± 9.35 × 10−5|0.07 ± 0.002|

The analysis presented mixed results. 𝐶2, 𝐶8 and 𝐶13 lost performance while 𝐶3 and 𝐶9 even improved their accuracy (AC) when validated with elderly people. However, all features significantly reduced their sensitivity (SE, true positive rate). These results coincide with those presented in [[8](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#B8-sensors-17-00198)]. It is noteworthy, as there are clear differences among the participants of both studies. The SisFall dataset we release in this work is intended to help develop fall detection algorithms for healthy independent elderly people, while authors in [[8](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#B8-sensors-17-00198)] obtained their dataset with highly impaired institutionalized Parkinson’s patients.

The generalized variation in sensitivity and specificity (which increased in validation with elderly people) suggests a shift in all activities with respect to the threshold. We performed a second comparative analysis to determine if the threshold is better adjusted when the algorithms are trained exclusively with elderly people. [Table 6](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#sensors-17-00198-t006) shows the validation accuracy of elderly people and threshold 𝑇1 values from the previous analysis (test 1), and a new analysis training the algorithms only with elderly people (test 2). As a result, all features improved their performance with the new training (first two columns). Additionally, all features diminished their 𝑇1 values, which confirms the shift between young and elderly people. This result makes evident the need of including data from elderly people in the training stage, especially because after training with elderly people, the accuracy was still below the one obtained with young people.

A close review of individual activities of SisFall provided the following findings: (_i_) ADLs and falls simulated by elderly people were smaller in amplitude than those simulated by young people. Then, algorithms trained with data from young people tended to bias the thresholds upwards in amplitude; (_ii_) most features tended to fail in the same activities. [Figure 4](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#sensors-17-00198-f004) shows box-plots of the maximum value obtained per activity with 𝐶8 feature (with young adults group exclusively). Note that only few activities severely crossed the threshold (horizontal red line): jogging quickly (D04), jump (D18), and falling backward when trying to sit (F11).

#### Figure 4.

[![Figure 4](https://cdn.ncbi.nlm.nih.gov/pmc/blobs/a489/5298771/f838d8c0c877/sensors-17-00198-g004.jpg)](https://www.ncbi.nlm.nih.gov/core/lw/2.0/html/tileshop_pmc/tileshop_pmc_inline.html?title=Click%20on%20image%20to%20zoom&p=PMC3&id=5298771_sensors-17-00198-g004.jpg)

Maximum value per activity obtained with 𝐶8. Most 𝑇1 threshold crossings (horizontal **red** line) are contained in activities D04, D18 and F11.

During this study, we observed differences in the way young adults behaved and fell with respect to elderly people. As previously stated by [[28](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#B28-sensors-17-00198)], the dynamics of simulated (mimicked) and real-world falls can be different. They found that young people simulating falls tend to do it faster without trying to avoid the impact. This behavior can be observed in the videos released as [Supplementary Materials](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#app1-sensors-17-00198) of this paper [[22](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#B22-sensors-17-00198)]. On the other hand, because of his age and experience in Judo, the elderly person that performed falls always tried to cushion the hits, which is what we expect from someone having an undesired fall.

We acknowledge that our dataset only includes simulated falls of one elderly person (subject SE06), who also is a Judo expert (not representative of the population). However, it allowed us to obtain five controlled repetitions of 15 different types of falls (for a total of 75 falls). Authors in [[8](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#B8-sensors-17-00198)] obtained 29 real falls, but they did not release them and their population was also distant from independent elderly people. Additionally, they did not provide detailed information about each fall condition. SisFall is the first public dataset that includes ADLs from elderly people and falls from an elderly person.

### 4.3. Zero False Negatives

One way to increase the effectiveness of the fall detection algorithms consists of including a false alarm button, which allows the user to cancel ADL detected as falls (false positives) [[29](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#B29-sensors-17-00198)]. This method allows moving the threshold just below the minimum fall values (as 𝑇2 does) [[12](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#B12-sensors-17-00198)]. [Table 7](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#sensors-17-00198-t007) shows the specificity and accuracy obtained after a 10-fold cross-validation with all 38 subjects (sensitivity achieved approx. 99.99% ± 0.2% in all features). The loss of performance in all features is evident, failing in up to seven of every 10 ADL, and achieving only 84% of accuracy with 𝐶9 (the best feature).

#### Table 7.

Specificity (SP) and accuracy (AC) after testing data from all subjects with threshold 𝑇2.

|Feature|SP|AC|
|---|---|---|
|𝐶2|32.97 ± 6.46|66.43 ± 3.06|
|𝐶3|59.04 ± 5.56|79.49 ± 2.70|
|𝐶8|38.34 ± 5.58|69.14 ± 2.71|
|𝐶9|67.97 ± 2.86|**83.96 ± 1.37**|
|𝐶13|37.80 ± 3.42|68.88 ± 1.69|

A fall detection system should not miss a single fall due to the medical implications every fall may carry on. Based on this statement, results with threshold 𝑇2 may be more meaningful than with 𝑇1. However, a failure rate of nearly 50/50 in ADL is prohibitive in real-life applications (the subject would be regularly pressing the false alarm button). The need of improving fall detection features stands, as a poor feature extraction requires more computationally intensive classifiers with the consequent battery life reduction [[11](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#B11-sensors-17-00198)].

## 5. Discussion

Research on elderly fall detection lacks public datasets with activities and falls simulated by elderly people. Available datasets have few activities and none include falls from the objective population. In this paper, we presented and made publicly available the SisFall dataset. It consisted of up to 34 activities (falls and ADLs) that were performed by 38 participants with a wearable device fixed to their waist. One of the participants was an elderly person that simulated both ADL and falls. Together with the dataset, we included videos of all simulated activities as an effort to help other researchers to replicate this work.

The SisFall dataset contains more participants, types of activities and recordings than any other publicly available dataset. It consists of 2706 ADL and 1798 falls, including data from 15 healthy independent elderly persons. To our knowledge, no public dataset contains data from elderly people, and their number of recordings is smaller (Mobifall: 342 ADLs and 288 falls; TFall: continuous ADLs and 240 falls; DLR: 961 ADLs and 56 falls; and Project Gravity: 138 ADLs and 72 falls).

We developed and released this dataset as a benchmark for other authors in the field. In that sense, we tested it with some of the most widely used features to detect falls, with three proof-of-principle experiments: the effect of the preprocessing stage, the importance of including data from elderly people, and how a threshold focused on maximum sensitivity severely reduces the specificity. Explanations about preprocessing are commonly simplified in most approaches available in the literature. Here, with a simple 4th order Butterworth filter, we increased the accuracy of several features. However, not all features improved their performance, which is expected as they share an integral-based nature; but it is a fact not previously discussed in the literature. Nevertheless, preprocessing is crucial in fall detection as it defines the minimum acquisition frequency, which, in this work, we found to be at 11 Hz for those features that indeed improved with the filtering stage.

In the second test, we analyzed the effect of training with young adults on a system developed to work with elderly people, which is usual in the field despite preliminary evidence that the results are biased [[8](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#B8-sensors-17-00198)]. Similar to this previous work, we found that the sensitivity is highly affected in all features once they are validated with the objective population. Note that Bagalà et al. [[8](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#B8-sensors-17-00198)] used 29 real falls of highly impaired Parkinson’s patients. In our case, we used 75 falls under controlled conditions from a single independent elderly person, which is also a martial arts expert. It is noteworthy that, despite the large difference among validation sets, our results presented the same trend of [[8](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#B8-sensors-17-00198)]. Moreover, when the classifiers were trained with elderly people, the accuracy was still lower than with young people. These findings suggest that, due to the overall higher acceleration that young people show in all activities, including ADLs, and falls from elderly people, it is crucial to obtain proper results. Additionally, the lower accuracy obtained when training with elderly people suggests that there is a need of a better feature extraction.

Developing a better feature extraction should be focused on specific activities. There are not many works focused on the types of falls elderly people suffer (most authors were limited to perform the same activities of previous works). However, the answers of our survey, previous works [[5](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#B5-sensors-17-00198)] and our findings suggest that if properly selected, authors could use a small sample of activities for their own tests. Performing an individual activity analysis (as presented in [Figure 4](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#sensors-17-00198-f004)) should help with the design of new features.

Our final test consisted of placing the threshold (𝑇2) below the fall value with minimum amplitude. In practice, fall detection systems are expected to detect all falls, while keeping the false positive rate as low as possible. Results of [Table 7](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#sensors-17-00198-t007) presented poor results in all features. Note how a not too large increment in sensitivity caused significant reductions in specificity. This fact is noteworthy, as most works focus on maximizing accuracy instead of favoring fall detection. Authors that addressed this issue usually included a false-alarm button as part of their methodology [[29](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#B29-sensors-17-00198)].

Our dataset may be biased by two facts: (_i_) all of our falls were simulated (mimicked). Klenk et al. [[28](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#B28-sensors-17-00198)] stated that young people tend to fall faster than in real-life conditions; (_ii_) we only included falls from one independent elderly person; and, as a martial arts expert, this subject is not representative of the population. With respect to the first fact, the results of [Section 4.2](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#sec4dot2-sensors-17-00198) show that training with young people effectively shows higher accelerations. However, this difference can be quantified and corrected by comparing their mean acceleration per activity versus the elderly subjects on the same dataset. About the second fact, our falls from an elderly person ([Section 4.2](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#sec4dot2-sensors-17-00198)) presented the same trend of a previous work that included real falls of impaired elderly people [[8](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#B8-sensors-17-00198)]. However, the crucial point here are the problems with obtaining real falls from healthy independent elderly people. In our case, we only had permission from the Ethics committee for simulating falls with one participant (SE06). Indeed, this participant always tried to soften the fall (as any person trying to avoid a fall would do). We consider that going farther with a wider and more realistic elderly fall dataset would be extremely challenging. Independent elderly people (the target of this work) fall on average once per year, i.e., to acquire a single fall would require a full year of continuous recording. Moreover, in this way, the actual conditions of the fall (activity, side of falling, etc.) may never be known. Despite these possible biases, we expect that this dataset will be a useful benchmark for other authors to test their own approaches and to solve the open issues presented in this work.

## 6. Conclusions

In this paper we presented and released SisFall, a fall and movement dataset acquired with 38 participants (15 of them elderly people). The data were acquired with an accelerometer fixed to their body. Along with this dataset we demonstrated that a 5 Hz fourth order filter keeps enough information for detecting falls on independent elderly people. Additionally, we showed that (as Bagalá et al. stated for institutionalized impaired elderly people) training fall detection algorithms with young people is not adequate for detecting falls on independent elderly people. The main problem found is that young people simulate falls and ADL with more acceleration than the expected with elderly people. Finally, we showed why finding maximum accuracy in fall detection algorithms is not a good measure for real-life applications, where the sensibility of the system must be fitted to detect falls, while reducing the false positive rate as possible. However, all tested features presented poor results with this requisite.

## Acknowledgments

We would like to thank Monica Rodriguez, Camilo Ocampo and Felipe Toro for their collaboration; and to all those anonymous participants, PROSA UDEA, and the Judo and Aikido martial arts groups at the UDEA for their insightful contribution in the generation of the SisFall dataset. We also want to acknowledge the dedication of the reviewers that evaluated this work. This work was supported by the project “Plataforma tecnológica para los servicios de teleasistencia, emergencias médicas, seguimiento y monitoreo permanente a los pacientes y apoyo a los programas de promoción y prevención”, code “Ruta-N: FP44842-512C-2013”.

## Supplementary Materials

The following files are available online [[22](https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/#B22-sensors-17-00198)]:

- **SisFall movement and fall dataset.** Text files with all recorded activities and a Readme with particular information of all subjects and recordings.
    
- **Video recordings of all activities.** Each activity included in the SisFall dataset was video recorded and included in this material.
    
- **Tables and figures with results of all features.** The same experiments shown along the paper with only five features were performed with the 14 selected for this work.
    

## Author Contributions

All authors conceived and designed the experiments; A.S. performed the experiments; A.S. and J.D.L. analyzed the data; and all authors read and approved the final manuscript.

## Conflicts of Interest

The authors declare no conflict of interest. The founding sponsors had no role in the design of the study; in the collection, analyses, or interpretation of data; in the writing of the manuscript, and in the decision to publish the results.

## References

- 1.Masdeu J., Sudarsky L., Wolfson L. Gait Disorders of Aging. Falls and Therapeutic Strategies. Lippincot-Raven; Philadelphia, PA, USA: 1997. [[Google Scholar](https://scholar.google.com/scholar_lookup?title=Gait%20Disorders%20of%20Aging.%20Falls%20and%20Therapeutic%20Strategies&author=J.%20Masdeu&author=L.%20Sudarsky&author=L.%20Wolfson&publication_year=1997&)]
- 2.Lord S., Sherrington C., Menz H. Falls in Older People: Risk Factors and Strategies for Prevention. 1st ed. Cambridge University Press; Cambridge, UK: 2001. [[Google Scholar](https://scholar.google.com/scholar_lookup?title=Falls%20in%20Older%20People:%20Risk%20Factors%20and%20Strategies%20for%20Prevention&author=S.%20Lord&author=C.%20Sherrington&author=H.%20Menz&publication_year=2001&)]
- 3.Vellas B., Wayne S., Romero L., Baumgartner R., Garry P. Fear of falling and restriction of mobility in elderly fallers. Age Ageing. 1997;26:189–193. doi: 10.1093/ageing/26.3.189. [[DOI](https://doi.org/10.1093/ageing/26.3.189)] [[PubMed](https://pubmed.ncbi.nlm.nih.gov/9223714/)] [[Google Scholar](https://scholar.google.com/scholar_lookup?journal=Age%20Ageing&title=Fear%20of%20falling%20and%20restriction%20of%20mobility%20in%20elderly%20fallers&author=B.%20Vellas&author=S.%20Wayne&author=L.%20Romero&author=R.%20Baumgartner&author=P.%20Garry&volume=26&publication_year=1997&pages=189-193&pmid=9223714&doi=10.1093/ageing/26.3.189&)]
- 4.Delbaere K., Crombez G., Vanderstraeten G., Willems T., Cambier D. Fear-related avoidance of activities, falls and physical frailty. A prospective community-based cohort study. Age Ageing. 2004;33:368–373. doi: 10.1093/ageing/afh106. [[DOI](https://doi.org/10.1093/ageing/afh106)] [[PubMed](https://pubmed.ncbi.nlm.nih.gov/15047574/)] [[Google Scholar](https://scholar.google.com/scholar_lookup?journal=Age%20Ageing&title=Fear-related%20avoidance%20of%20activities,%20falls%20and%20physical%20frailty.%20A%20prospective%20community-based%20cohort%20study&author=K.%20Delbaere&author=G.%20Crombez&author=G.%20Vanderstraeten&author=T.%20Willems&author=D.%20Cambier&volume=33&publication_year=2004&pages=368-373&pmid=15047574&doi=10.1093/ageing/afh106&)]
- 5.Lord S., Ward J., Williams P., Anstey K. An epidemiological study of falls in older community-dwelling women: The Randwick falls and fractures study. Aust. J. Public Health. 1993;17:240–245. doi: 10.1111/j.1753-6405.1993.tb00143.x. [[DOI](https://doi.org/10.1111/j.1753-6405.1993.tb00143.x)] [[PubMed](https://pubmed.ncbi.nlm.nih.gov/8286498/)] [[Google Scholar](https://scholar.google.com/scholar_lookup?journal=Aust.%20J.%20Public%20Health&title=An%20epidemiological%20study%20of%20falls%20in%20older%20community-dwelling%20women:%20The%20Randwick%20falls%20and%20fractures%20study&author=S.%20Lord&author=J.%20Ward&author=P.%20Williams&author=K.%20Anstey&volume=17&publication_year=1993&pages=240-245&pmid=8286498&doi=10.1111/j.1753-6405.1993.tb00143.x&)]
- 6.Igual R., Medrano C., Plaza I. Challenges, issues and trends in fall detection systems. BioMed. Eng. OnLine. 2013;12:1–24. doi: 10.1186/1475-925X-12-66. [[DOI](https://doi.org/10.1186/1475-925X-12-66)] [[PMC free article](https://pmc.ncbi.nlm.nih.gov/articles/PMC3711927/)] [[PubMed](https://pubmed.ncbi.nlm.nih.gov/23829390/)] [[Google Scholar](https://scholar.google.com/scholar_lookup?journal=BioMed.%20Eng.%20OnLine&title=Challenges,%20issues%20and%20trends%20in%20fall%20detection%20systems&author=R.%20Igual&author=C.%20Medrano&author=I.%20Plaza&volume=12&publication_year=2013&pages=1-24&pmid=23829390&doi=10.1186/1475-925X-12-66&)]
- 7.Brownsell S., Bradley D., Bragg R., Catlin P., Carlier J. Do community alarm users want telecare? J. Telemed. Telecare. 2000;6:199–204. doi: 10.1258/1357633001935356. [[DOI](https://doi.org/10.1258/1357633001935356)] [[PubMed](https://pubmed.ncbi.nlm.nih.gov/11027119/)] [[Google Scholar](https://scholar.google.com/scholar_lookup?journal=J.%20Telemed.%20Telecare&title=Do%20community%20alarm%20users%20want%20telecare?&author=S.%20Brownsell&author=D.%20Bradley&author=R.%20Bragg&author=P.%20Catlin&author=J.%20Carlier&volume=6&publication_year=2000&pages=199-204&pmid=11027119&doi=10.1258/1357633001935356&)]
- 8.Bagala F., Becker C., Cappello A., Chiari L., Aminian K., Hausdorff J.M., Zijlstra W., Klenk J. Evaluation of Accelerometer-Based Fall Detection Algorithms on Real-World Falls. PLoS ONE. 2012;7:e37062. doi: 10.1371/journal.pone.0037062. [[DOI](https://doi.org/10.1371/journal.pone.0037062)] [[PMC free article](https://pmc.ncbi.nlm.nih.gov/articles/PMC3353905/)] [[PubMed](https://pubmed.ncbi.nlm.nih.gov/22615890/)] [[Google Scholar](https://scholar.google.com/scholar_lookup?journal=PLoS%20ONE&title=Evaluation%20of%20Accelerometer-Based%20Fall%20Detection%20Algorithms%20on%20Real-World%20Falls&author=F.%20Bagala&author=C.%20Becker&author=A.%20Cappello&author=L.%20Chiari&author=K.%20Aminian&volume=7&publication_year=2012&pages=e37062&pmid=22615890&doi=10.1371/journal.pone.0037062&)]
- 9.Pannurat N., Thiemjarus S., Nantajeewarawat E. Automatic fall monitoring: A review. Sensors. 2014;14:12900–12936. doi: 10.3390/s140712900. [[DOI](https://doi.org/10.3390/s140712900)] [[PMC free article](https://pmc.ncbi.nlm.nih.gov/articles/PMC4166886/)] [[PubMed](https://pubmed.ncbi.nlm.nih.gov/25046016/)] [[Google Scholar](https://scholar.google.com/scholar_lookup?journal=Sensors&title=Automatic%20fall%20monitoring:%20A%20review&author=N.%20Pannurat&author=S.%20Thiemjarus&author=E.%20Nantajeewarawat&volume=14&publication_year=2014&pages=12900-12936&pmid=25046016&doi=10.3390/s140712900&)]
- 10.Shany T., Redmond S.J., Narayanan M.R., Lovell N.H. Sensors-Based Wearable Systems for Monitoring of Human Movement and Falls. IEEE Sens. J. 2012;12:658–670. doi: 10.1109/JSEN.2011.2146246. [[DOI](https://doi.org/10.1109/JSEN.2011.2146246)] [[Google Scholar](https://scholar.google.com/scholar_lookup?journal=IEEE%20Sens.%20J.&title=Sensors-Based%20Wearable%20Systems%20for%20Monitoring%20of%20Human%20Movement%20and%20Falls&author=T.%20Shany&author=S.J.%20Redmond&author=M.R.%20Narayanan&author=N.H.%20Lovell&volume=12&publication_year=2012&pages=658-670&doi=10.1109/JSEN.2011.2146246&)]
- 11.Habib M.A., Mohktar M.S., Kamaruzzaman S.B., Lim K.S., Pin T.M., Ibrahim F. Smartphone-Based Solutions for Fall Detection and Prevention: Challenges and Open Issues. Sensors. 2014;14:7181–7208. doi: 10.3390/s140407181. [[DOI](https://doi.org/10.3390/s140407181)] [[PMC free article](https://pmc.ncbi.nlm.nih.gov/articles/PMC4029687/)] [[PubMed](https://pubmed.ncbi.nlm.nih.gov/24759116/)] [[Google Scholar](https://scholar.google.com/scholar_lookup?journal=Sensors&title=Smartphone-Based%20Solutions%20for%20Fall%20Detection%20and%20Prevention:%20Challenges%20and%20Open%20Issues&author=M.A.%20Habib&author=M.S.%20Mohktar&author=S.B.%20Kamaruzzaman&author=K.S.%20Lim&author=T.M.%20Pin&volume=14&publication_year=2014&pages=7181-7208&pmid=24759116&doi=10.3390/s140407181&)]
- 12.Casilari E., Luque R., Morón M.J. Analysis of Android Device-Based Solutions for Fall Detection. Sensors. 2015;15:17827–17894. doi: 10.3390/s150817827. [[DOI](https://doi.org/10.3390/s150817827)] [[PMC free article](https://pmc.ncbi.nlm.nih.gov/articles/PMC4570297/)] [[PubMed](https://pubmed.ncbi.nlm.nih.gov/26213928/)] [[Google Scholar](https://scholar.google.com/scholar_lookup?journal=Sensors&title=Analysis%20of%20Android%20Device-Based%20Solutions%20for%20Fall%20Detection&author=E.%20Casilari&author=R.%20Luque&author=M.J.%20Mor%C3%B3n&volume=15&publication_year=2015&pages=17827-17894&pmid=26213928&doi=10.3390/s150817827&)]
- 13.Yuan J., Tan K.K., Lee T.H., Koh G.C.H. Power-Efficient Interrupt-Driven Algorithms for Fall Detection and Classification of Activities of Daily Living. IEEE Sens. J. 2015;15:1377–1387. doi: 10.1109/JSEN.2014.2357035. [[DOI](https://doi.org/10.1109/JSEN.2014.2357035)] [[Google Scholar](https://scholar.google.com/scholar_lookup?journal=IEEE%20Sens.%20J.&title=Power-Efficient%20Interrupt-Driven%20Algorithms%20for%20Fall%20Detection%20and%20Classification%20of%20Activities%20of%20Daily%20Living&author=J.%20Yuan&author=K.K.%20Tan&author=T.H.%20Lee&author=G.C.H.%20Koh&volume=15&publication_year=2015&pages=1377-1387&doi=10.1109/JSEN.2014.2357035&)]
- 14.O’Neill T., Varlow J., Silman A., Reeve J., Reid D., Todd C., Woolf A. Age and sex influences on fall characteristics. Ann. Rheum. Dis. 1994;53:773–775. doi: 10.1136/ard.53.11.773. [[DOI](https://doi.org/10.1136/ard.53.11.773)] [[PMC free article](https://pmc.ncbi.nlm.nih.gov/articles/PMC1005461/)] [[PubMed](https://pubmed.ncbi.nlm.nih.gov/7826141/)] [[Google Scholar](https://scholar.google.com/scholar_lookup?journal=Ann.%20Rheum.%20Dis.&title=Age%20and%20sex%20influences%20on%20fall%20characteristics&author=T.%20O%E2%80%99Neill&author=J.%20Varlow&author=A.%20Silman&author=J.%20Reeve&author=D.%20Reid&volume=53&publication_year=1994&pages=773-775&pmid=7826141&doi=10.1136/ard.53.11.773&)]
- 15.Vavoulas G., Pediaditis M., Chatzaki C., Spanakis E., Tsiknakis M. The MobiFall Dataset: Fall Detection and Classification with a Smartphone. Int. J. Monit. Surveill. Technol. Res. 2014;2:44–56. doi: 10.4018/ijmstr.2014010103. [[DOI](https://doi.org/10.4018/ijmstr.2014010103)] [[Google Scholar](https://scholar.google.com/scholar_lookup?journal=Int.%20J.%20Monit.%20Surveill.%20Technol.%20Res.&title=The%20MobiFall%20Dataset:%20Fall%20Detection%20and%20Classification%20with%20a%20Smartphone&author=G.%20Vavoulas&author=M.%20Pediaditis&author=C.%20Chatzaki&author=E.%20Spanakis&author=M.%20Tsiknakis&volume=2&publication_year=2014&pages=44-56&doi=10.4018/ijmstr.2014010103&)]
- 16.Medrano C., Igual R., Plaza I., Castro M. Detecting Falls as Novelties in Acceleration Patterns Acquired with Smartphones. PLoS ONE. 2014;9:e94811. doi: 10.1371/journal.pone.0094811. [[DOI](https://doi.org/10.1371/journal.pone.0094811)] [[PMC free article](https://pmc.ncbi.nlm.nih.gov/articles/PMC3988107/)] [[PubMed](https://pubmed.ncbi.nlm.nih.gov/24736626/)] [[Google Scholar](https://scholar.google.com/scholar_lookup?journal=PLoS%20ONE&title=Detecting%20Falls%20as%20Novelties%20in%20Acceleration%20Patterns%20Acquired%20with%20Smartphones&author=C.%20Medrano&author=R.%20Igual&author=I.%20Plaza&author=M.%20Castro&volume=9&publication_year=2014&pages=e94811&pmid=24736626&doi=10.1371/journal.pone.0094811&)]
- 17.Frank K., Vera M.J., Robertson P., Pfeifer T. Bayesian Recognition of Motion Related Activities with Inertial Sensors; Proceedings of the 12th ACM International Conference on Ubiquitous Computing (UbiComp); Copenhagen, Denmark. 26–29 September 2010; pp. 445–446. [[Google Scholar](https://scholar.google.com/scholar_lookup?journal=Proceedings%20of%20the%2012th%20ACM%20International%20Conference%20on%20Ubiquitous%20Computing%20\(UbiComp\)&title=Bayesian%20Recognition%20of%20Motion%20Related%20Activities%20with%20Inertial%20Sensors&author=K.%20Frank&author=M.J.%20Vera&author=P.%20Robertson&author=T.%20Pfeifer&pages=445-446&)]
- 18.Vilarinho T., Farshchian B., Bajer D.G., Dahl O.H., Egge I., Hegdal S.S., Lones A., Slettevold J.N., Weggersen S.M. A combined smartphone and smartwatch fall detection system; Proceedings of the IEEE International Conference on Computer and Information Technology; Ubiquitous Computing and Communications; Dependable, Autonomic and Secure Computing; Pervasive Intelligence and Computing; Liverpool, UK. 26–28 October 2015. [[Google Scholar](https://scholar.google.com/scholar_lookup?journal=Proceedings%20of%20the%20IEEE%20International%20Conference%20on%20Computer%20and%20Information%20Technology;%20Ubiquitous%20Computing%20and%20Communications;%20Dependable,%20Autonomic%20and%20Secure%20Computing;%20Pervasive%20Intelligence%20and%20Computing&title=A%20combined%20smartphone%20and%20smartwatch%20fall%20detection%20system&author=T.%20Vilarinho&author=B.%20Farshchian&author=D.G.%20Bajer&author=O.H.%20Dahl&author=I.%20Egge&)]
- 19.Igual R., Medrano C., Plaza I. A comparison of public datasets for acceleration-based fall detection. Med. Eng. Phys. 2015;37:870–878. doi: 10.1016/j.medengphy.2015.06.009. [[DOI](https://doi.org/10.1016/j.medengphy.2015.06.009)] [[PubMed](https://pubmed.ncbi.nlm.nih.gov/26233258/)] [[Google Scholar](https://scholar.google.com/scholar_lookup?journal=Med.%20Eng.%20Phys.&title=A%20comparison%20of%20public%20datasets%20for%20acceleration-based%20fall%20detection&author=R.%20Igual&author=C.%20Medrano&author=I.%20Plaza&volume=37&publication_year=2015&pages=870-878&pmid=26233258&doi=10.1016/j.medengphy.2015.06.009&)]
- 20.Reyna R., Palomera E., Gonzalez R., de Alba S.G., Clifford M. Human Fall Detection Using 3-Axis Accelerometer. Freescale Semiconductor; Austin, TX, USA: 2005. Technical Report. [[Google Scholar](https://scholar.google.com/scholar_lookup?title=Human%20Fall%20Detection%20Using%203-Axis%20Accelerometer&author=R.%20Reyna&author=E.%20Palomera&author=R.%20Gonzalez&author=S.G.%20de%20Alba&author=M.%20Clifford&publication_year=2005&)]
- 21.Tuck K. Motion and Freefall Detection Using the MMA8451, 2, 3Q. Freescale Semiconductor; Austin, TX, USA: 2011. Technical Report AN4070. [[Google Scholar](https://scholar.google.com/scholar_lookup?title=Motion%20and%20Freefall%20Detection%20Using%20the%20MMA8451,%202,%203Q&author=K.%20Tuck&publication_year=2011&)]
- 22.SISTEMIC: SisFall Dataset. [(accessed on 18 January 2017)]. Available online: [http://sistemic.udea.edu.co/investigacion/proyectos/english-falls/?lang=en](http://sistemic.udea.edu.co/investigacion/proyectos/english-falls/?lang=en).
- 23.Xue Y., Jin L. A Naturalistic 3D Acceleration-based Activity Dataset and Benchmark Evaluations; Proceedings of the IEEE International Conference on Systems Man and Cybernetics (SMC); Istanbul, Turkey. 10–13 October 2010; pp. 4081–4085. [[Google Scholar](https://scholar.google.com/scholar_lookup?journal=Proceedings%20of%20the%20IEEE%20International%20Conference%20on%20Systems%20Man%20and%20Cybernetics%20\(SMC\)&title=A%20Naturalistic%203D%20Acceleration-based%20Activity%20Dataset%20and%20Benchmark%20Evaluations&author=Y.%20Xue&author=L.%20Jin&pages=4081-4085&)]
- 24.Cleland I., Kikhia B., Nugent C., Boytsov A., Hallberg J., Synnes K., McClean S., Finlay D. Optimal Placement of Accelerometers for the Detection of Everyday Activities. Sensors. 2013;13:9183–9200. doi: 10.3390/s130709183. [[DOI](https://doi.org/10.3390/s130709183)] [[PMC free article](https://pmc.ncbi.nlm.nih.gov/articles/PMC3758644/)] [[PubMed](https://pubmed.ncbi.nlm.nih.gov/23867744/)] [[Google Scholar](https://scholar.google.com/scholar_lookup?journal=Sensors&title=Optimal%20Placement%20of%20Accelerometers%20for%20the%20Detection%20of%20Everyday%20Activities&author=I.%20Cleland&author=B.%20Kikhia&author=C.%20Nugent&author=A.%20Boytsov&author=J.%20Hallberg&volume=13&publication_year=2013&pages=9183-9200&pmid=23867744&doi=10.3390/s130709183&)]
- 25.López J.D., Ocampo C., Sucerquia A., Vargas-Bonilla F. Analyzing multiple accelerometer configurations to detect falls and motion; Proceedings of the Latin American Congress on Biomedical Engineering; Santander, Colombia. 26–28 October 2016. [[Google Scholar](https://scholar.google.com/scholar_lookup?journal=Proceedings%20of%20the%20Latin%20American%20Congress%20on%20Biomedical%20Engineering&title=Analyzing%20multiple%20accelerometer%20configurations%20to%20detect%20falls%20and%20motion&author=J.D.%20L%C3%B3pez&author=C.%20Ocampo&author=A.%20Sucerquia&author=F.%20Vargas-Bonilla&)]
- 26.Noury N., Fleury A., Rumeau P., Bourke A., Laighin G., Rialle V., Lundy J. Fall detection—Principles and Methods; Proceedings of the 29th Annual International Conference of the IEEE Engineering in Medicine and Biology Society; Lyon, France. 22–26 August 2007; pp. 1663–1666. [[DOI](https://doi.org/10.1109/IEMBS.2007.4352627)] [[PubMed](https://pubmed.ncbi.nlm.nih.gov/18002293/)] [[Google Scholar](https://scholar.google.com/scholar_lookup?journal=Proceedings%20of%20the%2029th%20Annual%20International%20Conference%20of%20the%20IEEE%20Engineering%20in%20Medicine%20and%20Biology%20Society&title=Fall%20detection%E2%80%94Principles%20and%20Methods&author=N.%20Noury&author=A.%20Fleury&author=P.%20Rumeau&author=A.%20Bourke&author=G.%20Laighin&pages=1663-1666&pmid=18002293&doi=10.1109/IEMBS.2007.4352627&)]
- 27.Noury N., Rumeau P., Bourke A., ÓLaighin G., Lundy J. A proposal for the classification and evaluation of fall detectors. IRBM. 2008;29:340–349. doi: 10.1016/j.irbm.2008.08.002. [[DOI](https://doi.org/10.1016/j.irbm.2008.08.002)] [[Google Scholar](https://scholar.google.com/scholar_lookup?journal=IRBM&title=A%20proposal%20for%20the%20classification%20and%20evaluation%20of%20fall%20detectors&author=N.%20Noury&author=P.%20Rumeau&author=A.%20Bourke&author=G.%20%C3%93Laighin&author=J.%20Lundy&volume=29&publication_year=2008&pages=340-349&doi=10.1016/j.irbm.2008.08.002&)]
- 28.Klenk J., Becker C., Lieken F., Nicolai S., Maetzler W., Alt W., Zijlstra W., Hausdorff J., van Lummel R., Chiari L., et al. Comparison of acceleration signals of simulated and real-world backward falls. Med. Eng. Phys. 2011;33:368–373. doi: 10.1016/j.medengphy.2010.11.003. [[DOI](https://doi.org/10.1016/j.medengphy.2010.11.003)] [[PubMed](https://pubmed.ncbi.nlm.nih.gov/21123104/)] [[Google Scholar](https://scholar.google.com/scholar_lookup?journal=Med.%20Eng.%20Phys.&title=Comparison%20of%20acceleration%20signals%20of%20simulated%20and%20real-world%20backward%20falls&author=J.%20Klenk&author=C.%20Becker&author=F.%20Lieken&author=S.%20Nicolai&author=W.%20Maetzler&volume=33&publication_year=2011&pages=368-373&pmid=21123104&doi=10.1016/j.medengphy.2010.11.003&)]
- 29.Koshmak G.A., Linden M., Loutfi A. Evaluation of the Android-Based Fall Detection System with Physiological Data Monitoring; Proceedings of the 35th Annual International Conference of the IEEE Engineering in Medicine and Biology Society (EMBC); Osaka, Japan. 3–7 July 2013; pp. 1164–1168. [[DOI](https://doi.org/10.1109/EMBC.2013.6609713)] [[PubMed](https://pubmed.ncbi.nlm.nih.gov/24109900/)] [[Google Scholar](https://scholar.google.com/scholar_lookup?journal=Proceedings%20of%20the%2035th%20Annual%20International%20Conference%20of%20the%20IEEE%20Engineering%20in%20Medicine%20and%20Biology%20Society%20\(EMBC\)&title=Evaluation%20of%20the%20Android-Based%20Fall%20Detection%20System%20with%20Physiological%20Data%20Monitoring&author=G.A.%20Koshmak&author=M.%20Linden&author=A.%20Loutfi&pages=1164-1168&pmid=24109900&doi=10.1109/EMBC.2013.6609713&)]