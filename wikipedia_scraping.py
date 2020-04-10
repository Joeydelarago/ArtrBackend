import re

import pymongo
import wikipedia
from nltk import bigrams
from pymongo import MongoClient

from artr_utilities import connect_to_mongodb, resume_from


def open_id_file():
    try:
        last_ids_file = open("txt_files/lasttitle.txt", "+r")
        lines = last_ids_file.read().splitlines()

        last_title = ""
        if len(lines) > 0:
            last_title = lines[-1]

        return open("txt_files/lasttitle.txt", "+w"), last_title

    except IOError:
        # File does not exist so it needs to be created
        last_ids_file = open("txt_files/lasttitle.txt", "+w")
        return last_ids_file, ""

def download_wiki_pages(collection):
    title_file, last_title = open_id_file()
    try:
        works = list(collection.sort([("title", pymongo.ASCENDING)]))

        if last_title != "":
            works = resume_from(last_title, works)
            print("Resuming from: " + last_title)

        for i in works:
            print(i["title"])
            results = wikipedia.search(i["title"], results=10)

            # Don't search paintings called self portrait
            if i["title"].lower() == "self-portrait" or "wiki_text" in i.keys():
                continue

            most_occurances = 0
            most_page = ""
            for page in results:
                try:
                    if page in ["self-portrait", "still life"]:
                        continue

                    p = wikipedia.page(page)
                    words = p.content.split()

                    num_occurances_painting = words.count('painting')

                    if num_occurances_painting > most_occurances:
                        most_occurances = num_occurances_painting
                        most_page = p
                except wikipedia.exceptions.PageError:
                    pass
                except wikipedia.exceptions.DisambiguationError:
                    pass
            if most_occurances > 5:
                summary = page.summary
                summary = re.sub("([\(\[]).*?([\)\]])", "", summary)
                summary = re.sub(r'[0-9]+', '', summary)
                summary = summary.replace(i["title"], "")
                artwork_collection.update({"_id": i["_id"]},
                                          {"$set": {"wiki_text": summary}})
                print(summary)
                print(most_page)
                break
            last_title = i["title"]
            print("-" * 100)

    finally:
        title_file.write(last_title)
        title_file.close()

def get_movements(collection):
    title_file, last_title = open_id_file()
    movements = []
    with open("txt_files/art_movements.txt", "r") as f:
        for movement in f:
            movements.append(movement.strip())
    print(movements)
    try:
        works = list(collection.sort([("title", pymongo.ASCENDING)]))

        if last_title != "":
            works = resume_from(last_title, works)
            print("Resuming from: " + last_title)

        for i in works:
            try:
                if i["wiki_text"] != "":
                    print(i["title"])
                    results = wikipedia.search(i["title"], results=10)

                    # Don't search paintings called self portrait
                    if i["title"].lower() == "self-portrait":
                        continue

                    for page in results:
                        try:
                            if page in ["self-portrait", "still life"]:
                                continue

                            p = wikipedia.page(page)
                            words = p.content.split()
                            num_occurances_painting = words.count('painting')

                            if num_occurances_painting > 2:
                                movement_dictionary = {i: 0 for i in movements}
                                for m in movements:
                                    movement_dictionary[m] = words.count(m)
                                top_value = sorted(movement_dictionary.copy(), key=movement_dictionary.get, reverse=True)[:1]
                                if movement_dictionary[top_value[0]] > 0:
                                    print("Yes")
                                    artwork_collection.update({"_id": i["_id"]},
                                                          {"$set": {"movement": top_value[0]}})
                                    continue
                        except wikipedia.exceptions.PageError:
                            pass
                        except wikipedia.exceptions.DisambiguationError:
                            pass
                    last_title = i["title"]
                    print("-" * 100)
            except Exception as e:
                pass


    finally:
        title_file.write(last_title)
        title_file.close()

def add_movement_text():
    movements = {'Baroque': """
    
The Raising of the Cross by Peter Paul Rubens (1610–1611)
Baroque painters worked deliberately to set themselves apart from the painters of the Renaissance and the Mannerism period after it. In their palette, they used intense and warm colours, and particularly made use of the primary colours red, blue and yellow, frequently putting all three in close proximity.[56] They avoided the even lighting of Renaissance painting and used strong contrasts of light and darkness on certain parts of the picture to direct attention to the central actions or figures. In their composition, they avoided the tranquil scenes of Renaissance paintings, and chose the moments of the greatest movement and drama. Unlike the tranquil faces of Renaissance paintings, the faces in Baroque paintings clearly expressed their emotions. They often used asymmetry, with action occurring away from the centre of the picture, and created axes that were neither vertical nor horizontal, but slanting to the left or right, giving a sense of instability and movement. They enhanced this impression of movement by having the costumes of the personages blown by the wind, or moved by their own gestures. The overall impressions were movement, emotion and drama.[57] Another essential element of baroque painting was allegory; every painting told a story and had a message, often encrypted in symbols and allegorical characters, which an educated viewer was expected to know and read.[58]


Las Meninas (1656) by Diego Velázquez
Early evidence of Italian Baroque ideas in painting occurred in Bologna, where Annibale Carracci, Agostino Carracci and Ludovico Carracci sought to return the visual arts to the ordered Classicism of the Renaissance. Their art, however, also incorporated ideas central the Counter-Reformation; these included intense emotion and religious imagery that appealed more to the heart than to the intellect.[59]

Another influential painter of the Baroque era was Michelangelo Merisi da Caravaggio. His realistic approach to the human figure, painted directly from life and dramatically spotlit against a dark background, shocked his contemporaries and opened a new chapter in the history of painting. Other major painters associated closely with the Baroque style include Artemisia Gentileschi, Guido Reni, Domenichino, Andrea Pozzo, and Paolo de Matteis in Italy; Francisco de Zurbarán and Diego Velázquez in Spain; Adam Elsheimer in Germany; and Nicolas Poussin and Georges de La Tour in France (though Poussin spent most of his working life in Italy). Poussin and La Tour adopted a "classical" Baroque style with less focus on emotion and greater attention to the line of the figures in the painting than to colour.


The Toilet of Venus by François Boucher (1755)
Peter Paul Rubens was the most important painter of the Flemish Baroque style. Rubens' highly charged compositions reference erudite aspects of classical and Christian history. His unique and immensely popular Baroque style emphasised movement, colour, and sensuality, which followed the immediate, dramatic artistic style promoted in the Counter-Reformation. Rubens specialized in making altarpieces, portraits, landscapes, and history paintings of mythological and allegorical subjects.

One important domain of Baroque painting was Quadratura, or paintings in trompe-l'oeil, which literally "fooled the eye". These were usually painted on the stucco of ceilings or upper walls and balustrades, and gave the impression to those on the ground looking up were that they were seeing the heavens populated with crowds of angels, saints and other heavenly figures, set against painted skies and imaginary architecture.[32]

In Italy, artists often collaborated with architects on interior decoration; Pietro da Cortona was one of the painters of the 17th century who employed this illusionist way of painting. Among his most important commissions were the frescoes he painted for the Palace of the Barberini family (1633–39), to glorify the reign of Pope Urban VIII. Pietro da Cortona's compositions were the largest decorative frescoes executed in Rome since the work of Michelangelo at the Sistine Chapel. .[60]

François Boucher was an important figure in the more delicate French Rococo style, which appeared during the late Baroque period. He designed tapestries, carpets and theatre decoration as well as painting. His work was extremely popular with Madame Pompadour, the Mistress of King Louis XV. His paintings featured mythological romantic, and mildly erotic themes.[61]
    """,
                 'Renaissance': """
                 Renaissance art is the painting, sculpture and decorative arts of the period of European history, emerging as a distinct style in Italy in about 1400, in parallel with developments which occurred in philosophy, literature, music, science and technology. Renaissance (meaning "rebirth") art, perceived as the noblest of ancient traditions, took as its foundation the art of Classical antiquity, but transformed that tradition by absorbing recent developments in the art of Northern Europe and by applying contemporary scientific knowledge. Renaissance art, with Renaissance humanist philosophy, spread throughout Europe, affecting both artists and their patrons with the development of new techniques and new artistic sensibilities. Renaissance art marks the transition of Europe from the medieval period to the Early Modern age.


Sandro Botticelli, The Birth of Venus, c. 1485. Uffizi, Florence
In many parts of Europe, Early Renaissance art was created in parallel with Late Medieval art. Renaissance art, painting, sculpture, architecture, music, and literature produced during the 14th, 15th, and 16th centuries in Europe under the combined influences of an increased awareness of nature, a revival of classical learning, and a more individualistic view of man. Scholars no longer believe that the Renaissance marked an abrupt break with medieval values, as is suggested by the French word renaissance, literally “rebirth.” Rather, historical sources suggest that interest in nature, humanistic learning, and individualism were already present in the late medieval period and became dominant in 15th- and 16th-century Italy, concurrently with social and economic changes such as the secularization of daily life, the rise of a rational money-credit economy, and greatly increased social mobility.

The influences upon the development of Renaissance men and women in the early 15th century are those that also affected philosophy, literature, architecture, theology, science, government, and other aspects of society. The following list presents a summary, dealt with more fully in the main articles that are cited above.

Classical texts, lost to European scholars for centuries, became available. These included Philosophy, Prose, Poetry, Drama, Science, a thesis on the Arts, and Early Christian Theology.
Simultaneously, Europe gained access to advanced mathematics which had its provenance in the works of Islamic scholars.
The advent of movable type printing in the 15th century meant that ideas could be disseminated easily, and an increasing number of books were written for a broad public.
The establishment of the Medici Bank and the subsequent trade it generated brought unprecedented wealth to a single Italian city, Florence.
Cosimo de' Medici set a new standard for patronage of the arts, not associated with the church or monarchy.
Humanist philosophy meant that man's relationship with humanity, the universe and with God was no longer the exclusive province of the Church.
A revived interest in the Classics brought about the first archaeological study of Roman remains by the architect Brunelleschi and sculptor Donatello. The revival of a style of architecture based on classical precedents inspired a corresponding classicism in painting and sculpture, which manifested itself as early as the 1420s in the paintings of Masaccio and Uccello.
The improvement of oil paint and developments in oil-painting technique by Dutch artists such as Robert Campin, Jan van Eyck, Rogier van der Weyden and Hugo van der Goes led to its adoption in Italy from about 1475 and had ultimately lasting effects on painting practices, worldwide.
The serendipitous presence within the region of Florence in the early 15th century of certain individuals of artistic genius, most notably Masaccio, Brunelleschi, Ghiberti, Piero della Francesca, Donatello and Michelozzo formed an ethos out of which sprang the great masters of the High Renaissance, as well as supporting and encouraging many lesser artists to achieve work of extraordinary quality.[1]
A similar heritage of artistic achievement occurred in Venice through the talented Bellini family, their influential in-law Mantegna, Giorgione, Titian and Tintoretto.[1][2][3]

                 """,
                 'Impressionism' : """
                 Impressionism is a 19th-century art movement characterized by relatively small, thin, yet visible brush strokes, open composition, emphasis on accurate depiction of light in its changing qualities (often accentuating the effects of the passage of time), ordinary subject matter, inclusion of movement as a crucial element of human perception and experience, and unusual visual angles. Impressionism originated with a group of Paris-based artists whose independent exhibitions brought them to prominence during the 1870s and 1880s.
The Impressionists faced harsh opposition from the conventional art community in France. The name of the style derives from the title of a Claude Monet work, Impression, soleil levant (Impression, Sunrise), which provoked the critic Louis Leroy to coin the term in a satirical review published in the Parisian newspaper Le Charivari.
The development of Impressionism in the visual arts was soon followed by analogous styles in other media that became known as impressionist music and impressionist literature.
                 """,
                 'Vanitas' : """
                 A vanitas is a symbolic work of art showing the transience of life, the futility of pleasure, and the certainty of death, often contrasting symbols of wealth and symbols of ephemerality and death. Best-known are vanitas still lifes, a common genre in Netherlandish art of the 16th and 17th centuries; they have also been created at other times and in other media and genres.[1]
                 Common vanitas symbols include skulls, which are a reminder of the certainty of death; rotten fruit (decay); bubbles (the brevity of life and suddenness of death); smoke, watches, and hourglasses (the brevity of life); and musical instruments (brevity and the ephemeral nature of life). Fruit, flowers and butterflies can be interpreted in the same way, and a peeled lemon was, like life, attractive to look at but bitter to taste. Art historians debate how much, and how seriously, the vanitas theme is implied in still-life paintings without explicit imagery such as a skull. As in much moralistic genre painting, the enjoyment evoked by the sensuous depiction of the subject is in a certain conflict with the moralistic message.[6]

Composition of flowers is a less obvious style of Vanitas by Abraham Mignon in the National Museum, Warsaw. Barely visible amid vivid and perilous nature (snakes, poisonous mushrooms), a bird skeleton is a symbol of vanity and shortness of life.
                 """,
                 'Bauhaus': """
                 The Staatliches Bauhaus (German: [ˈʃtaːtlɪçəs ˈbaʊˌhaʊs] (About this soundlisten)), commonly known as the Bauhaus, was a German art school operational from 1919 to 1933 that combined crafts and the fine arts.[1] The school became famous for its approach to design, which strove to combine beauty with usefulness and attempted to unify the principles of mass production with individual artistic vision.[1]

The Bauhaus was founded by architect Walter Gropius in Weimar. The German term Bauhaus—literally "building house"—was understood as meaning "School of Building", but in spite of its name the Bauhaus did not initially have an architecture department. Nonetheless, it was founded upon the idea of creating a Gesamtkunstwerk ("'total' work of art") in which all the arts, including architecture, would eventually be brought together. The Bauhaus style later became one of the most influential currents in modern design, Modernist architecture and art, design, and architectural education.[2] The Bauhaus movement had a profound influence upon subsequent developments in art, architecture, graphic design, interior design, industrial design, and typography.[3]

The school existed in three German cities—Weimar, from 1919 to 1925; Dessau, from 1925 to 1932; and Berlin, from 1932 to 1933—under three different architect-directors: Walter Gropius from 1919 to 1928; Hannes Meyer from 1928 to 1930; and Ludwig Mies van der Rohe from 1930 until 1933, when the school was closed by its own leadership under pressure from the Nazi regime, having been painted as a centre of communist intellectualism. Although the school was closed, the staff continued to spread its idealistic precepts as they left Germany and emigrated all over the world.[4]

The changes of venue and leadership resulted in a constant shifting of focus, technique, instructors, and politics. For example, the pottery shop was discontinued when the school moved from Weimar to Dessau, even though it had been an important revenue source; when Mies van der Rohe took over the school in 1930, he transformed it into a private school and would not allow any supporters of Hannes Meyer to attend it.


                 """,
                 'Expressionism': """
                 Expressionism is a modernist movement, initially in poetry and painting, originating in Germany at the beginning of the 20th century. Its typical trait is to present the world solely from a subjective perspective, distorting it radically for emotional effect in order to evoke moods or ideas.[1][2] Expressionist artists have sought to express the meaning[3] of emotional experience rather than physical reality.[3][4]

Expressionism developed as an avant-garde style before the First World War. It remained popular during the Weimar Republic,[1] particularly in Berlin. The style extended to a wide range of the arts, including expressionist architecture, painting, literature, theatre, dance, film and music.[5]

The term is sometimes suggestive of angst. In a historical sense, much older painters such as Matthias Grünewald and El Greco are sometimes termed expressionist, though the term is applied mainly to 20th-century works. The Expressionist emphasis on individual and subjective perspective has been characterized as a reaction to positivism and other artistic styles such as Naturalism and Impressionism.[6]
                 """,
                 'Tonalism': """Tonalism was an artistic style that emerged in the 1880s when American artists began to paint landscape forms with an overall tone of colored atmosphere or mist. Between 1880 and 1915, dark, neutral hues such as gray, brown or blue, often dominated compositions by artists associated with the style. During the late 1890s, American art critics began to use the term "tonal" to describe these works. Two of the leading associated painters were George Inness and James McNeill Whistler.

Tonalism is sometimes used to describe American landscapes derived from the French Barbizon style,[1] which emphasized mood and shadow. Tonalism was eventually eclipsed by Impressionism and European modernism.

Australian Tonalism emerged as an art movement in Melbourne during the 1910s.""",
                 'Mannerism': """Mannerism, also known as Late Renaissance,[1][2] is a style in European art that emerged in the later years of the Italian High Renaissance around 1520, spreading by about 1530 and lasting until about the end of the 16th century in Italy, when the Baroque style largely replaced it. Northern Mannerism continued into the early 17th century.[3]

Stylistically, Mannerism encompasses a variety of approaches influenced by, and reacting to, the harmonious ideals associated with artists such as Leonardo da Vinci, Raphael, and early Michelangelo. Where High Renaissance art emphasizes proportion, balance, and ideal beauty, Mannerism exaggerates such qualities, often resulting in compositions that are asymmetrical or unnaturally elegant.[4] The style is notable for its intellectual sophistication as well as its artificial (as opposed to naturalistic) qualities.[5] This artistic style privileges compositional tension and instability rather than the balance and clarity of earlier Renaissance painting. Mannerism in literature and music is notable for its highly florid style and intellectual sophistication.[6]

The definition of Mannerism and the phases within it continues to be a subject of debate among art historians. For example, some scholars have applied the label to certain early modern forms of literature (especially poetry) and music of the 16th and 17th centuries. The term is also used to refer to some late Gothic painters working in northern Europe from about 1500 to 1530, especially the Antwerp Mannerists—a group unrelated to the Italian movement. Mannerism has also been applied by analogy to the Silver Age of Latin literature.[7]""",
                 'Romanticism': """
                 Romanticism (also known as the Romantic era) was an artistic, literary, musical and intellectual movement that originated in Europe toward the end of the 18th century, and in most areas was at its peak in the approximate period from 1800 to 1850. Romanticism was characterized by its emphasis on emotion and individualism as well as glorification of all the past and nature, preferring the medieval rather than the classical. It was partly a reaction to the Industrial Revolution,[1] the aristocratic social and political norms of the Age of Enlightenment, and the scientific rationalization of nature—all components of modernity.[2] It was embodied most strongly in the visual arts, music, and literature, but had a major impact on historiography,[3] education,[4] the social sciences, and the natural sciences.[5][failed verification] It had a significant and complex effect on politics, with romantic thinkers influencing liberalism, radicalism, conservatism and nationalism.[6]

The movement emphasized intense emotion as an authentic source of aesthetic experience, placing new emphasis on such emotions as apprehension, horror and terror, and awe—especially that experienced in confronting the new aesthetic categories of the sublimity and beauty of nature. It elevated folk art and ancient custom to something noble, but also spontaneity as a desirable characteristic (as in the musical impromptu). In contrast to the Rationalism and Classicism of the Enlightenment, Romanticism revived medievalism[7] and elements of art and narrative perceived as authentically medieval in an attempt to escape population growth, early urban sprawl, and industrialism.

Although the movement was rooted in the German Sturm und Drang movement, which preferred intuition and emotion to the rationalism of the Enlightenment, the events and ideologies of the French Revolution were also proximate factors. Romanticism assigned a high value to the achievements of "heroic" individualists and artists, whose examples, it maintained, would raise the quality of society. It also promoted the individual imagination as a critical authority allowed of freedom from classical notions of form in art. There was a strong recourse to historical and natural inevitability, a Zeitgeist, in the representation of its ideas. In the second half of the 19th century, Realism was offered as a polar opposite to Romanticism.[8] The decline of Romanticism during this time was associated with multiple processes, including social and political changes and the spread of nationalism.[9]
The nature of Romanticism may be approached from the primary importance of the free expression of the feelings of the artist. The importance the Romantics placed on emotion is summed up in the remark of the German painter Caspar David Friedrich, "the artist's feeling is his law".[10] For William Wordsworth, poetry should begin as "the spontaneous overflow of powerful feelings", which the poet then "recollect[s] in tranquility", evoking a new but corresponding emotion the poet can then mold into art.[11]

To express these feelings, it was considered the content of art had to come from the imagination of the artist, with as little interference as possible from "artificial" rules dictating what a work should consist of. Samuel Taylor Coleridge and others believed there were natural laws the imagination—at least of a good creative artist—would unconsciously follow through artistic inspiration if left alone.[12] As well as rules, the influence of models from other works was considered to impede the creator's own imagination, so that originality was essential. The concept of the genius, or artist who was able to produce his own original work through this process of creation from nothingness, is key to Romanticism, and to be derivative was the worst sin.[13][14][15] This idea is often called "romantic originality".[16] Translator and prominent Romantic August Wilhelm Schlegel argued in his Lectures on Dramatic Arts and Letters that the most phenomenal power of human nature is its capacity to divide and diverge into opposite directions.[17]


William Blake, The Little Girl Found, from Songs of Innocence and Experience, 1794
Not essential to Romanticism, but so widespread as to be normative, was a strong belief and interest in the importance of nature. This particularly in the effect of nature upon the artist when he is surrounded by it, preferably alone. In contrast to the usually very social art of the Enlightenment, Romantics were distrustful of the human world, and tended to believe a close connection with nature was mentally and morally healthy. Romantic art addressed its audiences with what was intended to be felt as the personal voice of the artist. So, in literature, "much of romantic poetry invited the reader to identify the protagonists with the poets themselves".[18]

According to Isaiah Berlin, Romanticism embodied "a new and restless spirit, seeking violently to burst through old and cramping forms, a nervous preoccupation with perpetually changing inner states of consciousness, a longing for the unbounded and the indefinable, for perpetual movement and change, an effort to return to the forgotten sources of life, a passionate effort at self-assertion both individual and collective, a search after means of expressing an unappeasable yearning for unattainable goals".[19]
""",
                 'Romanesque': """
                 Romanesque art is the art of Europe from approximately 1000 AD to the rise of the Gothic style in the 12th century, or later, depending on region. The preceding period is known as the Pre-Romanesque period. The term was invented by 19th-century art historians, especially for Romanesque architecture, which retained many basic features of Roman architectural style – most notably round-headed arches, but also barrel vaults, apses, and acanthus-leaf decoration – but had also developed many very different characteristics. In Southern France, Spain and Italy there was an architectural continuity with the Late Antique, but the Romanesque style was the first style to spread across the whole of Catholic Europe, from Sicily to Scandinavia. Romanesque art was also greatly influenced by Byzantine art, especially in painting, and by the anti-classical energy of the decoration of the Insular art of the British Isles. From these elements was forged a highly innovative and coherent style.
                 Outside Romanesque architecture, the art of the period was characterised by a vigorous style in both sculpture and painting. The latter continued to follow essentially Byzantine iconographic models for the most common subjects in churches, which remained Christ in Majesty, the Last Judgment and scenes from the Life of Christ. In illuminated manuscripts more originality is seen, as new scenes needed to be depicted. The most lavishly decorated manuscripts of this period were bibles and psalters. The same originality applied to the capitals of columns: often carved with complete scenes with several figures. The large wooden crucifix was a German innovation at the very start of the period, as were free-standing statues of the enthroned Madonna. High relief was the dominant sculptural mode of the period.


Master of Pedret, The Virgin and Child in Majesty and the Adoration of the Magi, apse fresco from Tredòs, Val d'Aran, Catalonia, Spain, c. 1100, now at The Cloisters in New York City.
Colours were very striking, and mostly primary. In the 21st century: these colours can only be seen in their original brightness in stained glass, and a few well-preserved manuscripts. Stained glass became widely used, although survivals are sadly few. In an invention of the period, the tympanums of important church portals were carved with monumental schemes, often Christ in Majesty or the Last Judgement, but treated with more freedom than painted versions, as there were no equivalent Byzantine models.

Compositions usually had little depth, and needed to be flexible to be squeezed into the shapes of historiated initials, column capitals, and church tympanums; the tension between a tightly enclosing frame, from which the composition sometimes escapes, is a recurrent theme in Romanesque art. Figures often varied in size in relation to their importance. Landscape backgrounds, if attempted at all, were closer to abstract decorations than realism – as in the trees in the "Morgan Leaf". Portraiture hardly existed.
                 """,
                 'Realism': """
                 Realism was an artistic movement that emerged in France in the 1840s, around the 1848 Revolution.[1] Realists rejected Romanticism, which had dominated French literature and art since the early 19th century. Realism revolted against the exotic subject matter and the exaggerated emotionalism and drama of the Romantic movement. Instead, it sought to portray real and typical contemporary people and situations with truth and accuracy, and not avoiding unpleasant or sordid aspects of life. The movement aimed to focus on unidealized subjects and events that were previously rejected in art work. Realist works depicted people of all classes in situations that arise in ordinary life, and often reflected the changes brought by the Industrial and Commercial Revolutions. Realism was primarily concerned with how things appeared to the eye, rather than containing ideal representations of the world.[2] The popularity of such "realistic" works grew with the introduction of photography—a new visual source that created a desire for people to produce representations which look objectively real.

The Realists depicted everyday subjects and situations in contemporary settings, and attempted to depict individuals of all social classes in a similar manner. Gloomy earth toned palettes were used to ignore beauty and idealization that was typically found in art. This movement sparked controversy because it purposefully criticized social values and the upper classes, as well as examining the new values that came along with the industrial revolution. Realism is widely regarded as the beginning of the modern art movement due to the push to incorporate modern life and art together.[3] Classical idealism and Romantic emotionalism and drama were avoided equally, and often sordid or untidy elements of subjects were not smoothed over or omitted. Social realism emphasizes the depiction of the working class, and treating them with the same seriousness as other classes in art, but realism, as the avoidance of artificiality, in the treatment of human relations and emotions was also an aim of Realism. Treatments of subjects in a heroic or sentimental manner were equally rejected.[4]

Realism as an art movement was led by Gustave Courbet in France. It spread across Europe and was influential for the rest of the century and beyond, but as it became adopted into the mainstream of painting it becomes less common and useful as a term to define artistic style. After the arrival of Impressionism and later movements which downgraded the importance of precise illusionistic brushwork, it often came to refer simply to the use of a more traditional and tighter painting style. It has been used for a number of later movements and trends in art, some involving careful illusionistic representation, such as Photorealism, and others the depiction of "realist" subject matter in a social sense, or attempts at both.
                 """}

    artwork_collection, _ = connect_to_mongodb()
    count = 0
    for work in artwork_collection.find({}).sort([("title", pymongo.ASCENDING)]):
        try:
            if work['movement'] != None :
                count += 1
                print(work["title"])
                artwork_collection.update({"_id": work["_id"]},
                                          {"$set": {"movement_text": movements[work['movement']]}})
        except Exception:
            pass
    print(count)


if __name__ == "__main__":
    artwork_collection, user_collection = connect_to_mongodb()
    add_movement_text()



