# Conducteur 2026-12-ep-s2a-resumer-des-donnees (EN) : « Mean, median, histogram: summarizing data without being fooled »

Généré depuis `contenus/fiches/2026-12-ep-s2a-resumer-des-donnees.yaml` (102 scènes, données fictives). Pour chaque scène : type, univers visuel, texte à l'écran, animation, légendes successives, puis la voix off. Les calculs écrits à l'écran apparaissent terme à terme pendant que la voix les dit.

### 1. accroche
- Écran : Twenty employees. *Which tells the truth*: the mean or the median?
- Voix : Twenty employees. One question: how long does it take them to get to work? The mean says just over 21 minutes. Yet half of them take 20 minutes or less. And if just one employee moves far away, the mean jumps… while almost nothing changes for anyone else. Which number tells the truth?

### 2. accueil
- Écran : Hi, and *welcome*!
- Voix : Hi, and welcome! Thanks for being here. Salaries, grades, commuting times: we sum everything up with an average. In this episode, we'll see when it tells the truth, when it misleads, and what to use instead.

### 3. animation
- Écran : What you'll *learn*
- Animation « apercu » : cartes=[{'icone': 'tableau', 'texte': 'Build a frequency *table*'}, {'icone': 'histogramme', 'texte': 'Choose and read a *histogram*'}, {'icone': 'forme', 'texte': "Recognise a distribution's *shape*"}, {'icone': 'equilibre', 'texte': 'Compute a *mean*'}, {'icone': 'mediane', 'texte': 'Find the *median*'}, {'icone': 'laboratoire', 'texte': 'Test it in the *lab*, then practise'}]
- Voix : By the end, you'll be able to summarize a data set, read its distribution and choose between mean and median. In practice: build a frequency table; choose and read a histogram; recognise the shape of a distribution; compute a mean, and see why it's a balance point; find a median; and check it all yourself, with two labs and a worked exercise.

### 4. titre 1
- Écran : Counting: counts, frequencies, cumulative
- Voix : A thousand answers to a survey: nobody is going to read them one by one. To learn the method, let's start with a small class of twenty-five pupils. How do you sum up their answers?

### 5. titre 1.1
- Écran : Counting: the counts
- Voix : Step one is very simple: count.

### 6. courbe
- Écran : How many *brothers and sisters*? Class of 25
- Graphique barres : points [[0, 5], [1, 10], [2, 6], [3, 4]]
- Note à l'écran : Another example, to learn the method: a fictional class of 25 pupils.
- Voix : We ask twenty-five pupils how many brothers and sisters they have. Five have none, ten have one, six have two and four have three. These numbers are called counts.

### 7. texte
- Écran : Always check the *total*: 5 + 10 + 6 + 4 = 25
- Voix : First habit: check the total. Five plus ten plus six plus four does make twenty-five. Without the total, a count doesn't mean much.

### 8. titre 1.2
- Écran : Dividing by the total: frequencies
- Voix : Step two: divide each count by the total.

### 9. formule
- Écran : Frequency = count ÷ total
- Formule : ['\\text{frequency}=\\dfrac{\\text{count}}{\\text{total count}}', '\\dfrac{10}{25}=0.40=40\\%']
- Voix : The frequency is the count divided by the total. For the pupils with one brother or sister: ten divided by twenty-five is zero point four zero, or forty percent.

### 10. etapes
- Écran : The full table
  - 0: 5 pupils, or *20%*
  - 1: 10 pupils, or *40%*
  - 2: 6 pupils, or *24%*
  - 3: 4 pupils, or *16%*
- Voix : Here is the full table. No brothers or sisters: five pupils, or twenty percent. One: ten pupils, or forty percent. Two: six pupils, or twenty-four percent. Three: four pupils, or sixteen percent.

### 11. texte
- Écran : Frequencies always add up to *100%*
- Voix : Frequencies always add up to one hundred percent. If they don't, someone is missing, or rounding got in the way.

### 12. titre 1.3
- Écran : Adding up: cumulative frequencies
- Voix : Step three: cumulative frequencies.

### 13. etapes
- Écran : *At most* so many brothers and sisters
  - At most 0: *20%*
  - At most 1: 20 + 40 = *60%*
  - At most 2: 60 + 24 = *84%*
  - At most 3: 84 + 16 = *100%*
- Voix : We add the frequencies as we go. At most zero brothers or sisters: twenty percent. At most one: twenty plus forty, sixty percent. At most two: sixty plus twenty-four, eighty-four percent. At most three: one hundred percent, the whole class.

### 14. chiffre
- Écran : of pupils have *at most two* brothers and sisters
- Chiffre clé : 84
- Note à l'écran : Cumulating follows the order of the values: it makes sense here because 0, 1, 2, 3 are ordered.
- Voix : One sentence now sums up the class: eighty-four percent of the pupils have at most two brothers and sisters. Cumulating makes sense here because the values come in order.

### 15. titre 1.4
- Écran : The trap: comparing counts
- Voix : One last point, and it is the most common trap.

### 16. etapes
- Écran : Two classes, *two sizes*
  - Class A, 25 pupils: 10 have one brother or sister, *40%*
  - Class B, 40 pupils: 12 have one, *30%*
- Voix : Let's compare two classes. In class A, with twenty-five pupils, ten have exactly one brother or sister, or forty percent. In class B, with forty pupils, there are twelve, only thirty percent.

### 17. texte
- Écran : 12 is more than 10, but *30% is less than 40%*
- Voix : Twelve is more than ten. But relative to the size of the class, it is less. To compare groups of different sizes, compare frequencies, not counts.

### 18. exercice
- Écran : 20 employees: *8 car*, *6 public transport*, *4 bike*, *2 walk*. Frequencies? Does a cumulative total make sense?
- Voix : Your turn. Twenty employees say how they get to work: eight by car, six by public transport, four by bike and two on foot. Work out the frequencies. Then ask yourself: would a cumulative total make sense here?

### 19. correction
  - Car 8 ÷ 20 = *40%*, public transport 6 ÷ 20 = *30%*
  - Bike 4 ÷ 20 = *20%*, walk 2 ÷ 20 = *10%*
  - Cumulative: *no meaning*, these categories have no order
- Réponse : Total 100%; no cumulative without an order
- Voix : Here's the answer. Car: eight divided by twenty, forty percent; public transport: thirty percent. Bike: twenty percent; walking: ten percent. And the cumulative total? It has no meaning here: ways of getting to work have no natural order. The total is one hundred percent, and we only accumulate values that can be ranked, like a number of siblings or durations.

### 20. texte
- Écran : Keep these *20 employees* in mind
- Voix : Keep these twenty employees in mind: we'll follow them to the end of the episode. First, let's draw their answers.

### 21. titre 2
- Écran : Drawing: bar chart or histogram
- Voix : Two charts made of bars. On one, the bars touch; on the other, they don't. That detail changes how you read them.

### 22. titre 2.1
- Écran : The bar chart: categories
- Voix : Let's start with the bar chart.

### 23. courbe
- Écran : How *20 employees* get to work
- Graphique barres : points [[0, 8], [1, 6], [2, 4], [3, 2]]
- Note à l'écran : Fictional company of 20 employees (chapter 1 exercise).
- Voix : Here are the twenty employees from the chapter 1 exercise. One bar for each way of getting to work: car, public transport, bike, walking. The bars are separate, because these are distinct categories. You could put them in another order without changing the meaning.

### 24. titre 2.2
- Écran : The histogram: numbers in classes
- Voix : Now let's take a numerical variable: commuting time, in minutes.

### 25. courbe
- Écran : Commuting time, *10-minute classes*
- Graphique histogramme : points [[0, 3], [10, 7], [20, 6], [30, 3], [40, 1]]
- Note à l'écran : Fictional commuting times of the same 20 employees.
- Voix : We group the commuting times into ten-minute classes. Three employees take under ten minutes, seven between ten and twenty, six between twenty and thirty, three between thirty and forty, and just one between forty and fifty. This time the bars touch: minutes run on continuously, with no gap between classes. Each bin includes its left edge but not its right one: a 20-minute trip counts in the 20-to-30 bin.

### 26. courbe
- Écran : The same times, *20-minute classes*
- Graphique histogramme : points [[0, 10], [20, 9], [40, 1]]
- Voix : These are exactly the same data, grouped into twenty-minute classes. Ten employees take under twenty minutes, nine between twenty and forty, only one over forty. The peak between ten and twenty minutes has vanished.

### 27. texte
- Écran : The choice of classes *changes the shape*
- Voix : The choice of classes changes the shape. Too wide, and they hide the details. Too narrow, and they show bumps that are just chance. When you see a histogram, always check the width of the classes.

### 28. titre 2.3
- Écran : Unequal widths: area = count
- Voix : One last trap: classes of different widths.

### 29. courbe
- Écran : *Misleading build*: height = count, unequal classes
- Graphique histogramme : points [[0, 3], [10, 7], [20, 10]]
- Voix : Now let's put everything over twenty minutes into a single class, from twenty to fifty. It holds ten employees. If we use the count as the height, this big bar dwarfs the rest: long commutes seem to dominate.

### 30. formule
- Écran : The right height: *density*
- Formule : ['\\text{density}=\\dfrac{\\text{count}}{\\text{class width}}', '\\dfrac{10}{30}\\approx 0.33\\ \\text{employee per minute}']
- Voix : In a histogram, the area stands for the count. So the height must be a density: the count divided by the width of the class. For the class from twenty to fifty minutes: ten divided by thirty, about zero point three three employee per minute.

### 31. animation
- Écran : Height = *density*: the picture is right again
- Animation « densite » : bornes=[0, 10, 20, 50], effectifs=[3, 7, 10], unite=minutes
  - Height = count: the wide bin *crushes everything*
  - Height = *density*: the same spacing everywhere
  - Area = density × width = *count*
- Voix : Back to the misleading build: with the count as the height, the big twenty-to-fifty-minute bin crushes everything. Let's switch to density: the bars rise or fall, and the dots, one per employee, take the same spacing everywhere; the ten-to-twenty-minute bin is the densest again. Each bar's area gives back its count: zero point three times ten, three; zero point seven times ten, seven; a third times thirty, ten.

### 32. exercice
- Écran : 40 visitors: *aged 0–20: 8*, *20–30: 12*, *30–60: 20*. Which class is densest?
- Voix : Your turn. Forty visitors to a fictional museum: eight are aged zero to twenty, twelve are twenty to thirty, twenty are thirty to sixty. A histogram that uses the count as height highlights the thirty to sixty group. Is it right? Which class is the densest?

### 33. correction
  - Aged 0–20: 8 ÷ 20 = *0.4* visitor per year of age
  - Aged 20–30: 12 ÷ 10 = *1.2* visitors per year of age
  - Aged 30–60: 20 ÷ 30 ≈ *0.67* visitor per year of age
- Réponse : Ages 20–30: the densest class
- Voix : Divide each count by the width of its class. Zero to twenty: eight divided by twenty, zero point four visitor per year of age. Twenty to thirty: twelve divided by ten, one point two. Thirty to sixty: twenty divided by thirty, about zero point six seven. The densest class is twenty to thirty: the histogram based on counts was misleading.

### 34. texte
- Écran : What if we changed the bins *ourselves*?
- Voix : Before reading the shape, let's change the bins ourselves.

### 35. titre 2.4 · univers immersif (fond sombre)
- Écran : Lab: bin width
- Voix : Lab time. Let's take the twenty travel times and change the bin width ourselves.

### 36. animation · univers immersif (fond sombre)
- Écran : *20-minute* bins
- Animation « pastilles » : valeurs=[4, 7, 9, 11, 12, 14, 15, 16, 18, 19, 21, 23, 25, 26, 27, 29, 32, 35, 38, 44], largeur_classe=20, unite=minutes
- Voix : Twenty-minute bins: ten, nine, one. The peak has gone.

### 37. animation · univers immersif (fond sombre)
- Écran : *10-minute* bins
- Animation « pastilles » : valeurs=[4, 7, 9, 11, 12, 14, 15, 16, 18, 19, 21, 23, 25, 26, 27, 29, 32, 35, 38, 44], largeur_classe=10, unite=minutes
- Voix : Ten-minute bins: three, seven, six, three, one. A clear hump.

### 38. animation · univers immersif (fond sombre)
- Écran : *5-minute* bins: two 'peaks'?
- Animation « pastilles » : valeurs=[4, 7, 9, 11, 12, 14, 15, 16, 18, 19, 21, 23, 25, 26, 27, 29, 32, 35, 38, 44], largeur_classe=5, unite=minutes
- Voix : Five-minute bins. The fifteen-minute trip counts in the fifteen-to-twenty bin: the left edge is included. Two peaks appear, at fifteen and at twenty-five minutes. They rest on one or two employees. Too wide, bins hide; too narrow, they invent.

### 39. courbe
- Écran : Ages of 40 visitors: *height = count*
- Graphique histogramme : points [[0, 8], [20, 12], [30, 20]]
- Voix : Second setting: the ages of forty visitors, in unequal bins. With the count as the height, the thirty-to-sixty group dominates.

### 40. courbe
- Écran : Height = *count density*
- Graphique histogramme : points [[0, 0.4], [20, 1.2], [30, 0.6667]]
- Note à l'écran : Areas: 0.4 × 20 = 8; 1.2 × 10 = 12; ⅔ × 30 = 20; total 40 (height 0.67 rounded).
- Voix : We switch to count density: the count divided by the width, in visitors per year of age. Zero point four, one point two, about zero point six seven. The densest bin is twenty to thirty. And each rectangle's area gives back its count: one point two times ten years, twelve visitors. The total area is forty, the number of visitors.

### 41. titre 3
- Écran : Reading the shape of a distribution
- Voix : Before you calculate anything, look at the shape of a histogram. It already tells you a lot.

### 42. animation · univers immersif (fond sombre)
- Écran : Our *20 employees*: one hump, a small right tail
- Animation « pastilles » : valeurs=[4, 7, 9, 11, 12, 14, 15, 16, 18, 19, 21, 23, 25, 26, 27, 29, 32, 35, 38, 44], largeur_classe=10, unite=minutes
  - One dot per employee
  - A *hump* between 10 and 30 minutes
  - A small right *tail*: 44 minutes
- Voix : Back to our twenty employees. Their histogram has one hump, between ten and thirty minutes, and a small right tail: the employee who takes forty-four minutes. That's a property of these made-up data, not a law of real commutes.

### 43. titre 3.1
- Écran : Symmetric: two similar sides
- Voix : First shape, the simplest one.

### 44. courbe
- Écran : Marks of *20 pupils*, out of 20
- Graphique histogramme : points [[0, 1], [4, 4], [8, 10], [12, 4], [16, 1]]
- Note à l'écran : Fictional marks of 20 pupils.
- Voix : Here are the fictional marks of twenty pupils. One peak in the middle, between eight and twelve, and two sides that mirror each other. In this example, the distribution is roughly symmetric. Here, the middle sums up the group well.

### 45. titre 3.2
- Écran : Skewed: a long tail
- Voix : Second shape: the skewed distribution.

### 46. courbe
- Écran : Monthly incomes of *25 people*
- Graphique histogramme : points [[0, 2], [1000, 9], [2000, 6], [3000, 3], [4000, 2], [5000, 1], [6000, 1], [7000, 1]]
- Note à l'écran : Fictional incomes of 25 people, classes of €1,000.
- Voix : Here are fictional monthly incomes. Most people are on the left, between one thousand and three thousand euros. Then a long tail stretches to the right: a few very high incomes. This is called right skew.

### 47. etapes
- Écran : A tail, *on one side or the other*
  - Tail *on the right*: a few very large values
  - Tail *on the left*: a few very small values
- Voix : A tail can go either way. On the right, it points to a few very large values, like high incomes. On the left, a few very small values. What a tail does to the mean, we'll see in chapter 5.

### 48. titre 3.3
- Écran : Two peaks: two groups?
- Voix : Third shape, the most surprising one.

### 49. courbe
- Écran : Heights of *44 adults*
- Graphique histogramme : points [[150, 2], [155, 6], [160, 9], [165, 5], [170, 6], [175, 9], [180, 5], [185, 2]]
- Note à l'écran : Fictional heights of 44 adults, women and men mixed.
- Voix : Here are the fictional heights of forty-four adults. Two peaks: one around one hundred and sixty centimetres, the other around one hundred and seventy-five. We call this distribution bimodal. One possible explanation: a mix of two groups with different average heights, for example women and men. The histogram alone doesn't prove it: you need other information.

### 50. texte
- Écran : Two peaks? Check whether *several groups* are mixed
- Voix : If two groups are mixed, a single 'central' number would describe neither. Remember this reflex: two peaks can signal a mix of groups. Check it with other information, then separate them before summarizing.

### 51. courbe
- Écran : Shape *A*
- Graphique histogramme : points [[0, 1], [1, 1], [2, 2], [3, 3], [4, 5], [5, 8], [6, 10], [7, 6]]
- Voix : Shape A: a tail to the left.

### 52. courbe
- Écran : Shape *B*
- Graphique histogramme : points [[0, 1], [1, 3], [2, 6], [3, 9], [4, 9], [5, 6], [6, 3], [7, 1]]
- Voix : Shape B: two similar sides.

### 53. courbe
- Écran : Shape *C*
- Graphique histogramme : points [[0, 2], [1, 7], [2, 9], [3, 4], [4, 4], [5, 9], [6, 7], [7, 2]]
- Voix : Shape C: two peaks.

### 54. courbe
- Écran : Shape *D*
- Graphique histogramme : points [[0, 6], [1, 10], [2, 8], [3, 5], [4, 3], [5, 2], [6, 1], [7, 1]]
- Voix : Shape D: a tail to the right.

### 55. exercice
- Écran : Shapes *A*, *B*, *C*, *D*: age at death, income, exam marks, heights?
- Voix : Your turn. Here are four shapes, A, B, C and D. And four variables: age at death, income, exam marks, adult heights. Match each variable to its shape.

### 56. correction
  - Exam marks: *B*, roughly symmetric
  - Income: *D*, right tail
  - Age at death: *A*, left tail
  - Adult heights: *C*, two peaks
- Réponse : Every shape has an explanation
- Voix : Here's the answer. Exam marks, shape B: often roughly symmetric. Income, shape D: a right tail, because of a few very high incomes. Age at death, shape A: where most deaths happen at an old age, a tail towards younger ages. Adult heights, shape C: two peaks, probably a mix of women and men. Behind every shape there is an explanation.

### 57. texte
- Écran : One number to sum it up: *the mean*?
- Voix : We can see the shape. Now let's put it into a single number. The first that comes to mind: the mean.

### 58. titre 4
- Écran : What the mean really says
- Voix : “On average.” You read it in every article. But what exactly does it mean?

### 59. titre 4.1
- Écran : The mean, an equal share
- Voix : Let's start with a simple picture: sharing.

### 60. etapes
- Écran : Four friends, *one shared pot*
  - They have €5, €10, €15 and €30
  - All in the pot: *€60*
  - Split four ways: *€15 each*
- Voix : Four friends pool their money. They have five, ten, fifteen and thirty euros. In the pot, that makes sixty euros. Shared equally between the four, that is fifteen euros each: that's the mean.

### 61. formule
- Écran : Mean = *sum ÷ count*
- Formule : ['\\text{mean}=\\dfrac{\\text{sum of the values}}{\\text{number of values}}', '\\dfrac{5+10+15+30}{4}=\\dfrac{60}{4}=15']
- Voix : Hence the formula: the mean is the sum of the values divided by how many there are. Here, sixty divided by four: fifteen.

### 62. titre 4.2
- Écran : The Σ notation, step by step
- Voix : In textbooks, this formula is written with a scary-looking symbol. There is nothing complicated about it.

### 63. formule
- Écran : Σ means *“add up”*
- Formule : ['\\bar{x}=\\dfrac{x_1+x_2+x_3+x_4}{4}', '\\bar{x}=\\dfrac{1}{n}\\times\\sum_{i=1}^{n}x_i']
- Voix : We call the values x one, x two, x three, x four, and the mean x bar. The sigma symbol tells you to add up all the values, from the first to the n-th. Then divide that sum by n, the number of values. It is exactly the shared pot calculation.

### 64. titre 4.3
- Écran : The balance point
- Voix : A second way to see the mean: a balance point.

### 65. animation
- Écran : The mean, a *balance point*
- Animation « equilibre » : valeurs=[5, 10, 15, 30], unite=€
  - Four friends: *€5, €10, €15 and €30*
  - Pivot at *€15*: the plank balances
  - The deviations *cancel out*: they sum to 0
- Voix : Let's put the four amounts from the kitty on a plank: five, ten, fifteen and thirty euros. For the plank to stay level, the pivot must sit exactly at the mean, fifteen euros. There, the deviations cancel out: minus ten and minus five on one side, plus fifteen on the other, zero in total; that's always true for the mean, and a single value far away is enough to shift the balance.

### 66. titre 4.4
- Écran : The weighted mean
- Voix : And what if the values don't all count the same?

### 67. formule
- Écran : 14 in maths, *weight 3*; 10 in French, *weight 1*
- Formule : ['\\dfrac{14\\times 3+10\\times 1}{3+1}', '=\\dfrac{52}{4}=13']
- Voix : A pupil gets fourteen in maths, with a weight of three, and ten in French, with a weight of one. Multiply each mark by its weight, add them up, then divide by the sum of the weights. Fourteen times three plus ten, fifty-two, divided by four: thirteen.

### 68. texte
- Écran : Without weights: 12. With them: *13*
- Voix : Without the weights, we would have found twelve. The weighted mean gives more weight to what matters most: here, maths.

### 69. exercice
- Écran : Class of *10 pupils*: mean 12. Class of *30 pupils*: mean 8. Overall mean?
- Voix : Your turn. A class of ten pupils has a mean mark of twelve. A class of thirty pupils has a mean of eight. What is the overall mean of the forty pupils?

### 70. correction
  - 10 × 12 = 120 points and 30 × 8 = 240 points
  - (120 + 240) ÷ 40 = *9*
- Réponse : 9, not 10
- Voix : Let's work it out. The first class has ten times twelve, one hundred and twenty points; the second, thirty times eight, two hundred and forty points. Three hundred and sixty points for forty pupils: a mean of nine. Not ten, which would be the mean of the two means: the big class weighs three times as much.

### 71. chiffre
- Écran : the mean falls *in the dip*, between the two peaks
- Chiffre clé : 170
- Note à l'écran : Approximate mean from bin midpoints: about 169.8 cm.
- Voix : Remember the two-peaked heights. We only know the bins, so we take the middle of each bin, for example a hundred and fifty-two and a half for the bin from a hundred and fifty to a hundred and fifty-five, as the value of its adults. That gives an approximate mean of about a hundred and seventy centimetres. It falls in the dip, where there are few people: a mean can describe no one.

### 72. chiffre
- Écran : the mean trip of our *20 employees*
- Chiffre clé : 21.25
- Note à l'écran : Total of the 20 trips: 425 minutes; 425 ÷ 20 = 21.25.
- Voix : And our twenty employees? Their trips add up to 425 minutes. Divided by twenty, that's twenty-one and a quarter minutes. It's what each would have if the total of individual durations were shared equally. That total adds up separate trips: it isn't time spent together.

### 73. texte
- Écran : 21.25 min: a *typical* employee's trip?
- Voix : 21.25 minutes. Is that a typical employee's trip? Not necessarily.

### 74. titre 5
- Écran : Mean or median?
- Voix : Why do most people earn less than the average salary? It sounds impossible. And yet it happens all the time.

### 75. exercice
- Écran : In a group, what share of people earn *less than the mean*?
- Voix : Here's a question to start. In a group of workers, what share earn less than the average salary? Less than half, exactly half, or more than half? Hold on to your answer.

### 76. titre 5.1
- Écran : The mean
- Voix : Let's start with the mean.

### 77. texte
- Écran : Nine customers in a café earn between *€1,600* and *€2,800* a month
- Note à l'écran : €1,600 · 1,800 · 1,900 · 2,000 · 2,200 · 2,300 · 2,500 · 2,700 · 2,800
- Voix : Nine customers are sitting in a café. They earn between one thousand six hundred and two thousand eight hundred euros a month.

### 78. formule
- Écran : Their *mean* salary
- Formule : ['\\mathrm{mean}=\\dfrac{\\mathrm{total}}{\\mathrm{count}}', '=\\dfrac{19{,}800}{9}=2{,}200']
- Note à l'écran : In euros per month.
- Voix : The mean is the total divided by the number of people. Together they earn nineteen thousand eight hundred euros. Divide by nine, and you get two thousand two hundred euros.

### 79. texte
- Écran : A tenth customer walks in. He earns *€200,000* a month.
- Voix : The door opens. A tenth customer walks in, and he earns two hundred thousand euros a month.

### 80. formule
- Écran : The mean *shoots up*
- Formule : ['\\dfrac{19{,}800+200{,}000}{10}', '=21{,}980']
- Voix : Let's do the sum again. Nineteen thousand eight hundred plus two hundred thousand, divided by ten. The café's mean salary jumps to twenty-one thousand nine hundred eighty euros.

### 81. chiffre
- Écran : of the customers now earn *less than the mean*
- Chiffre clé : 90
- Note à l'écran : 9 customers out of 10.
- Voix : Nine customers out of ten now earn less than the mean. Nobody's pay has changed. One extreme value has dragged the mean upward.

### 82. titre 5.2
- Écran : The median
- Voix : There's another summary that holds up much better: the median.

### 83. etapes
- Écran : Finding the median
  - Put the values *in order*
  - Odd number of values: take *the middle one*
  - Even number: average *the two in the middle*
- Voix : Finding the median takes three steps. First, put the values in order, from smallest to largest. With an odd number of values, the median is the one in the middle. With an even number, you take the average of the two middle values.

### 84. animation
- Écran : The median *by elimination*
- Animation « elimination » : valeurs=[1600, 1800, 1900, 2000, 2200, 2300, 2500, 2700, 2800], ajout=200000, unite=€
  - Nine salaries, *sorted*
  - Cross out the *lowest* and the *highest*
  - The *middle* is left: the 5th value
  - The *€200,000* customer walks in
  - Ten values: the mean of the *two middle ones*
- Voix : Back to the café: let's sort its first nine salaries, from lowest to highest. Cross out the lowest and the highest, then again, two by two. The fifth value is left, two thousand two hundred euros: that's the median, at position n plus one over two. The rich customer walks in, with two hundred thousand euros: there are now ten salaries. Cross out two by two again, and two are left, the fifth and the sixth: the median is their mean, two thousand two hundred and fifty euros.

### 85. etapes
- Écran : One extreme value
  - Mean: from €2,200 to *€21,980*
  - Median: from €2,200 to *€2,250*
- Voix : Compare the two. One extreme value pushes the mean from two thousand two hundred to almost twenty-two thousand euros. The median goes up by just fifty euros.

### 86. courbe
- Écran : The ten salaries, *lowest to highest*
- Graphique points : points [[1, 1600], [2, 1800], [3, 1900], [4, 2000], [5, 2200], [6, 2300], [7, 2500], [8, 2700], [9, 2800], [10, 200000]]
- Note à l'écran : Nine salaries clustered at the bottom, a single one at the top.
- Voix : Let's line up the ten salaries, from lowest to highest: nine stay clustered together, and the median stays with them, at two thousand two hundred fifty euros. The tenth, two hundred thousand euros, single-handedly drags the mean up to twenty-one thousand nine hundred eighty euros, above nine salaries out of ten.

### 87. etapes
- Écran : Mean and median depend on the *shape* of the distribution
  - Long tail toward high values: mean *often above* the median
  - Symmetric distribution: mean *close to* the median
  - Long tail toward low values: mean *often below* the median
- Voix : This is a common tendency, not a law: it all depends on the shape of the distribution. When a few very large values form a long tail toward the top, as salaries and wealth often do, the mean often ends up above the median. When the distribution is perfectly symmetric, they coincide; when it is roughly symmetric, they are close. And when the tail points toward low values, the mean often falls below the median.

### 88. texte
- Écran : Mean above the median: *at least half* of the values are below the mean
- Voix : That answers the challenge. By definition, at least half of the values are less than or equal to the median. So if the mean is above the median, at least half of the values are below the mean. For salaries, that means at least half of workers, and often many more.

### 89. exercice
- Écran : Seven salaries: €1,500, 1,600, 1,700, 1,800, 1,900, 2,000, 2,100. Mean and median, before and after a *€20,000* salary joins?
- Voix : Your turn. Seven monthly salaries: one thousand five hundred, one thousand six hundred, one thousand seven hundred, one thousand eight hundred, one thousand nine hundred, two thousand, and two thousand one hundred euros. Work out the mean and the median. Then do it again after a salary of twenty thousand euros joins the group.

### 90. correction
  - Before: 12,600 ÷ 7 = *€1,800*; median *€1,800*
  - After: 32,600 ÷ 8 = *€4,075*
  - Median: (1,800 + 1,900) ÷ 2 = *€1,850*
- Réponse : The mean more than doubles, the median gains €50
- Voix : Here's the solution. Before, the total is twelve thousand six hundred euros. Divided by seven, the mean is one thousand eight hundred euros, the same as the median, the fourth value. Afterwards, the total is thirty-two thousand six hundred euros, divided by eight: four thousand seventy-five euros. With eight values, the median is the average of the fourth and fifth: one thousand eight hundred fifty euros. The mean has more than doubled, while the median gained only fifty euros.

### 91. titre 5.3
- Écran : Which one should you use?
- Voix : The mean is sensitive to extreme values: a single very large value can pull it upwards. The median, by contrast, is determined by the middle position in the ordered data. That does not make it universally better: the right measure depends on the question we want to answer.

### 92. etapes
- Écran : Each summary answers *its own* question
  - "What does a typical worker earn?" → the *median*
  - "What do all the salaries cost?" → the *mean*, × headcount
  - The most honest choice: report *both*
- Voix : Each summary answers its own question. To know what a typical worker earns, the median is the right answer. To know what all the salaries cost together, you need the mean, multiplied by the number of workers. The median can't tell you that. The most honest choice is often to report both, because the gap between them tells you on its own whether the distribution is skewed.

### 93. texte
- Écran : The median has a blind spot: it ignores *how big* the gaps are
- Note à l'écran : If the customer earned €2 million a month, the café's median would still be €2,250.
- Voix : The median has a blind spot too: it ignores how big the gaps are. Whether the rich customer earns two hundred thousand euros or two million, the café's median stays the same. It shows the centre, but not how spread out the values are: two groups can share the same median and have very different inequality.

### 94. titre 5.4 · univers immersif (fond sombre)
- Écran : Lab: a single extreme value
- Voix : Second lab. Let's move a single value and watch who follows.

### 95. animation · univers immersif (fond sombre)
- Écran : The tenth customer: *slider* from €2,300 to €200,000
- Animation « curseur » : valeurs=[1600, 1800, 1900, 2000, 2200, 2300, 2500, 2700, 2800, 2300], indice=9, vers=200000, axe_max=3600, unite=€, decimales=0
  - Nine salaries, and a *tenth customer* at €2,300
  - Median: *€2,250*
  - Mean: *€2,210*
  - The tenth climbs to €200,000: the mean *flies off*, the median *stays*
- Voix : The café's nine salaries, and a tenth customer whose salary we raise. At each position, we sort the ten salaries again and recompute. At two thousand three hundred euros: mean two thousand two hundred and ten, median two thousand two hundred and fifty. At fifty thousand: mean six thousand nine hundred and eighty, median still two thousand two hundred and fifty. At two hundred thousand: mean twenty-one thousand nine hundred and eighty. The median doesn't move: from two thousand three hundred up, the tenth customer sorts after the sixth salary, so the two middle values stay two thousand two hundred and two thousand three hundred.

### 96. animation · univers immersif (fond sombre)
- Écran : One employee *moves*: 44 → 120 minutes
- Animation « curseur » : valeurs=[4, 7, 9, 11, 12, 14, 15, 16, 18, 19, 21, 23, 25, 26, 27, 29, 32, 35, 38, 44], indice=19, vers=120, axe_max=55, unite=minutes, decimales=2
  - The same *20 employees*
  - Median: *20 min*
  - Mean: *21.25 min*
  - 44 → 120 minutes: mean *25.05 min*, median *20 min*
- Voix : Back to the company. No one is added: the employee who took forty-four minutes moves and now takes one hundred and twenty. Still the same twenty employees. The mean goes from twenty-one and a quarter to twenty-five point zero five minutes. The median stays at twenty minutes. One individual moved, and only the mean followed.

### 97. etapes
- Écran : Key takeaways
  - Compare *frequencies*, not counts
  - Unequal bins: *area* counts
  - Look at the *shape* before any calculation
  - Mean: an *equal share* of the total
  - Median: splits in *two*; right tail, mean often above
- Voix : What to remember. One: count, then divide by the total; compare frequencies, not counts. Two: separate bars for categories, a histogram for numbers, and when bins are unequal, area is what counts. Three: look at the shape before any calculation; two peaks may mean two groups. Four: the mean is the total divided by the count, what each would get with an equal share; one extreme value moves it. Five: the median splits the data in half; with a right tail, the mean usually sits above the median. Pick the one that answers your question.

### 98. exercice
- Écran : 10 trips: 5, 8, 12, 15, 15, 18, 22, 25, 30, *90* min. Share under 20 min, shape, mean, median?
- Voix : Your turn. Ten employees at a fictional branch take, in minutes: 5, 8, 12, 15, 15, 18, 22, 25, 30 and 90. One: what share takes under 20 minutes? Two: what shape is this distribution? Three: compute the mean and the median. Four: how many employees are below the mean, and which number would you report as the 'typical trip'? Pause the video.

### 99. correction
  - Under 20 min: 6 out of 10, *60%*
  - Shape: *right tail* (the 90-minute trip)
  - Mean: 240 ÷ 10 = *24 min*
  - Median: (15 + 18) ÷ 2 = *16.5 min*
- Voix : One: 6 out of 10, so 60% (5, 8, 12, 15, 15 and 18). Two: a right tail, caused by the 90-minute trip. Three: total 240, mean 240 ÷ 10 = 24 minutes; ten values, so the median is the average of the 5th and 6th: (15 + 18) ÷ 2 = 16.5 minutes.

### 100. etapes
- Écran : Answer (continued)
  - 7 out of 10 below the mean: typical trip *16.5 min*
  - If 90 were a typo for 35: mean *18.5 min*, median unchanged
- Voix : Four: 7 employees out of 10 are below the mean; the typical trip is the median, 16.5 minutes. Going further: if the 90 minutes were a typo for 35, the mean would drop to 18.5 minutes and the median would not move.

### 101. cloture
- Écran : Next episode: *spread*. A question? *Ask in the comments*
- Voix : That's it: next time someone quotes an average salary or an average waiting time, you'll know which question to ask. But two teams can share the same median and have very different trips: that's what the next episode, on spread, is all about. If this video was useful, subscribe, leave a like and share it with someone it will help. And if an exercise gets the better of you, write to us in the comments: we'll help you, for free. Thanks for watching, see you very soon!

### 102. fin
- Écran : Enlightening through numbers.
- Voix : ACTU-BASICS. Enlightening through numbers.
