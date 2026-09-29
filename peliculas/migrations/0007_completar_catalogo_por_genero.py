from django.db import migrations
from django.db.models import Count


PELICULAS_POR_GENERO = {
    'accion': [
        ('Mad Max: Fury Road', 'George Miller', 2015, 'En un desierto devastado, Max y Furiosa emprenden una peligrosa huida para escapar de un tirano.'),
        ('John Wick', 'Chad Stahelski', 2014, 'Un antiguo asesino regresa al mundo criminal cuando su vida tranquila es destruida.'),
        ('Die Hard', 'John McTiernan', 1988, 'Un policía enfrenta a un grupo armado que toma un rascacielos durante una celebración.'),
        ('Terminator 2: Judgment Day', 'James Cameron', 1991, 'Un joven y su protector intentan evitar un futuro dominado por máquinas.'),
        ('Mission: Impossible - Fallout', 'Christopher McQuarrie', 2018, 'Ethan Hunt y su equipo buscan recuperar material nuclear antes de que caiga en malas manos.'),
        ('Top Gun: Maverick', 'Joseph Kosinski', 2022, 'Un piloto veterano prepara a un grupo de aviadores para una misión de alto riesgo.'),
        ('Kill Bill: Vol. 1', 'Quentin Tarantino', 2003, 'Una mujer despierta de un largo coma y emprende la búsqueda de quienes la traicionaron.'),
        ('The Raid: Redemption', 'Gareth Evans', 2011, 'Un equipo policial queda atrapado en un edificio controlado por una organización criminal.'),
        ('Casino Royale', 'Martin Campbell', 2006, 'James Bond afronta una partida de póker decisiva contra un financista del terrorismo.'),
        ('Dredd', 'Pete Travis', 2012, 'Un juez y su aprendiz quedan sitiados en una torre dominada por una banda.'),
        ('Crouching Tiger, Hidden Dragon', 'Ang Lee', 2000, 'Una espada legendaria desaparece y desencadena una búsqueda entre guerreros.'),
        ('The Bourne Identity', 'Doug Liman', 2002, 'Un hombre sin memoria descubre que posee habilidades extraordinarias y busca su identidad.'),
    ],
    'aventura': [
        ('Raiders of the Lost Ark', 'Steven Spielberg', 1981, 'Indiana Jones compite con agentes nazis por encontrar un antiguo objeto religioso.'),
        ('Pirates of the Caribbean: The Curse of the Black Pearl', 'Gore Verbinski', 2003, 'Un herrero y un capitán pirata se embarcan para rescatar a una joven de una tripulación maldita.'),
        ('Life of Pi', 'Ang Lee', 2012, 'Un joven náufrago comparte un bote salvavidas con un tigre en medio del océano.'),
        ('The Mummy', 'Stephen Sommers', 1999, 'Una expedición despierta accidentalmente a una antigua criatura en el desierto.'),
        ('The Goonies', 'Richard Donner', 1985, 'Un grupo de amigos sigue un mapa que podría salvar sus hogares y conducir a un tesoro.'),
        ('The Princess Bride', 'Rob Reiner', 1987, 'Un joven campesino atraviesa un reino lleno de peligros para reunirse con su amor.'),
        ('The Hobbit: An Unexpected Journey', 'Peter Jackson', 2012, 'Bilbo Bolsón acompaña a un grupo de enanos en la búsqueda de su hogar perdido.'),
        ('Jumanji: Welcome to the Jungle', 'Jake Kasdan', 2017, 'Cuatro estudiantes quedan dentro de un videojuego y deben completar una misión para salir.'),
        ('The Chronicles of Narnia: The Lion, the Witch and the Wardrobe', 'Andrew Adamson', 2005, 'Cuatro hermanos descubren un reino mágico al atravesar un ropero.'),
        ('The Secret Life of Walter Mitty', 'Ben Stiller', 2013, 'Un empleado reservado sale de viaje para encontrar una fotografía desaparecida.'),
        ('Journey to the Center of the Earth', 'Eric Brevig', 2008, 'Un científico y sus acompañantes exploran un mundo oculto bajo la superficie terrestre.'),
        ('The Lost City of Z', 'James Gray', 2016, 'Un explorador británico organiza expediciones para encontrar una antigua ciudad amazónica.'),
    ],
    'comedia': [
        ('Groundhog Day', 'Harold Ramis', 1993, 'Un meteorólogo revive una y otra vez el mismo día en un pequeño pueblo.'),
        ('Superbad', 'Greg Mottola', 2007, 'Dos amigos intentan disfrutar de una última fiesta antes de terminar la escuela.'),
        ('Bridesmaids', 'Paul Feig', 2011, 'Una mujer intenta cumplir su papel de dama de honor mientras atraviesa cambios personales.'),
        ('The Grand Budapest Hotel', 'Wes Anderson', 2014, 'Un conserje y su joven ayudante se ven envueltos en un robo y una disputa familiar.'),
        ('Home Alone', 'Chris Columbus', 1990, 'Un niño olvidado en casa prepara ingeniosas defensas contra dos ladrones.'),
        ('Mean Girls', 'Mark Waters', 2004, 'Una adolescente descubre las reglas y rivalidades sociales de su nueva escuela.'),
        ('Some Like It Hot', 'Billy Wilder', 1959, 'Dos músicos se disfrazan para escapar de unos criminales y terminan en una banda de jazz.'),
        ('Airplane!', 'Jim Abrahams, David Zucker, Jerry Zucker', 1980, 'Un ex piloto debe ayudar a aterrizar un avión cuando la tripulación enferma.'),
        ('The Big Lebowski', 'Joel Coen', 1998, 'Un hombre apodado el Nota busca resolver un caso de identidad confundida.'),
        ('Paddington 2', 'Paul King', 2017, 'Paddington busca un regalo especial y debe resolver el misterio de un robo.'),
        ('The Intouchables', 'Olivier Nakache, Eric Toledano', 2011, 'La amistad inesperada entre un aristócrata y su nuevo cuidador cambia sus rutinas.'),
        ("Ferris Bueller's Day Off", 'John Hughes', 1986, 'Un estudiante decide saltarse las clases y disfrutar de un día en la ciudad.'),
    ],
    'drama': [
        ('The Shawshank Redemption', 'Frank Darabont', 1994, 'Un banquero condenado a prisión construye una amistad y mantiene la esperanza durante décadas.'),
        ("Schindler's List", 'Steven Spielberg', 1993, 'Un empresario alemán utiliza su fábrica para proteger a trabajadores judíos durante la guerra.'),
        ('Whiplash', 'Damien Chazelle', 2014, 'Un joven baterista busca destacar bajo la exigencia extrema de su instructor.'),
        ('A Beautiful Mind', 'Ron Howard', 2001, 'Un matemático brillante enfrenta desafíos personales mientras desarrolla su carrera.'),
        ('Moonlight', 'Barry Jenkins', 2016, 'Tres momentos de la vida de un joven muestran su crecimiento y búsqueda de identidad.'),
        ('The Pianist', 'Roman Polanski', 2002, 'Un músico polaco lucha por sobrevivir durante la ocupación de Varsovia.'),
        ('12 Angry Men', 'Sidney Lumet', 1957, 'Un jurado debate un caso y examina sus dudas antes de llegar a un veredicto.'),
        ('Manchester by the Sea', 'Kenneth Lonergan', 2016, 'Un hombre regresa a su pueblo natal y debe hacerse cargo de su sobrino.'),
        ('The Father', 'Florian Zeller', 2020, 'Un hombre mayor y su hija afrontan los efectos de la pérdida de memoria.'),
        ('The Pursuit of Happyness', 'Gabriele Muccino', 2006, 'Un padre y su hijo buscan estabilidad mientras atraviesan una etapa de dificultades.'),
        ('Cinema Paradiso', 'Giuseppe Tornatore', 1988, 'Un cineasta recuerda su infancia y la amistad que nació en una sala de cine.'),
        ('Green Book', 'Peter Farrelly', 2018, 'Un pianista y su conductor recorren el sur de Estados Unidos durante una gira.'),
    ],
    'terror': [
        ('Psycho', 'Alfred Hitchcock', 1960, 'Una viajera llega a un motel aislado cuyo dueño guarda secretos inquietantes.'),
        ('The Exorcist', 'William Friedkin', 1973, 'Una familia busca ayuda cuando una niña comienza a mostrar cambios inexplicables.'),
        ('Get Out', 'Jordan Peele', 2017, 'Una visita familiar se transforma en una experiencia cada vez más perturbadora.'),
        ('Hereditary', 'Ari Aster', 2018, 'Una familia descubre secretos oscuros después de una pérdida.'),
        ('The Thing', 'John Carpenter', 1982, 'Un equipo aislado en la Antártida sospecha que algo puede imitar a sus integrantes.'),
        ('Halloween', 'John Carpenter', 1978, 'Una noche de Halloween, una joven es perseguida por un hombre que escapó de una institución.'),
        ('It', 'Andy Muschietti', 2017, 'Un grupo de niños se enfrenta a una presencia que adopta la forma de sus mayores temores.'),
        ('A Quiet Place', 'John Krasinski', 2018, 'Una familia intenta sobrevivir en silencio ante criaturas atraídas por el sonido.'),
        ('The Conjuring', 'James Wan', 2013, 'Dos investigadores paranormales ayudan a una familia que vive en una casa aterradora.'),
        ('Scream', 'Wes Craven', 1996, 'Un grupo de jóvenes intenta descubrir quién se esconde tras una serie de ataques.'),
        ('The Babadook', 'Jennifer Kent', 2014, 'Una madre y su hijo enfrentan una presencia vinculada a un misterioso libro infantil.'),
        ('The Ring', 'Gore Verbinski', 2002, 'Una periodista investiga una cinta de video relacionada con una leyenda aterradora.'),
    ],
    'scifi': [
        ('Blade Runner', 'Ridley Scott', 1982, 'Un detective recibe la tarea de localizar androides fugitivos en una ciudad futurista.'),
        ('Arrival', 'Denis Villeneuve', 2016, 'Una lingüista intenta comunicarse con visitantes extraterrestres recién llegados a la Tierra.'),
        ('Dune', 'Denis Villeneuve', 2021, 'Paul Atreides llega a un planeta desértico clave para el futuro de su familia.'),
        ('2001: A Space Odyssey', 'Stanley Kubrick', 1968, 'Una misión espacial investiga un objeto enigmático que aparece en distintos momentos de la historia.'),
        ('E.T. the Extra-Terrestrial', 'Steven Spielberg', 1982, 'Un niño ayuda a un visitante de otro mundo a encontrar el camino de regreso.'),
        ('Ex Machina', 'Alex Garland', 2014, 'Un programador participa en una prueba para evaluar una inteligencia artificial avanzada.'),
        ('Children of Men', 'Alfonso Cuarón', 2006, 'En un futuro sin nacimientos, un hombre protege a una mujer que podría cambiarlo todo.'),
        ('The Fifth Element', 'Luc Besson', 1997, 'Un taxista y una misteriosa joven buscan reunir los elementos necesarios para salvar el mundo.'),
        ('Gravity', 'Alfonso Cuaron', 2013, 'Dos astronautas luchan por regresar a casa después de un accidente en órbita.'),
        ('Minority Report', 'Steven Spielberg', 2002, 'Un agente de una unidad policial futurista es acusado de un crimen que aún no ha ocurrido.'),
        ('Moon', 'Duncan Jones', 2009, 'Un trabajador solitario en la Luna se acerca al final de su turno y descubre algo inesperado.'),
        ('Edge of Tomorrow', 'Doug Liman', 2014, 'Un oficial revive el mismo día de una batalla contra una fuerza invasora.'),
    ],
    'romance': [
        ('Pride & Prejudice', 'Joe Wright', 2005, 'Elizabeth Bennet y Mr. Darcy revisan sus primeras impresiones mientras sus familias se cruzan.'),
        ('Before Sunrise', 'Richard Linklater', 1995, 'Dos jóvenes que se conocen en un tren pasan una noche conversando por Viena.'),
        ('Eternal Sunshine of the Spotless Mind', 'Michel Gondry', 2004, 'Una pareja intenta borrar sus recuerdos y descubre lo que aún los une.'),
        ('When Harry Met Sally...', 'Rob Reiner', 1989, 'Dos amigos discuten durante años si la amistad puede convivir con el amor.'),
        ('Notting Hill', 'Roger Michell', 1999, 'Un librero londinense conoce a una estrella de cine y ambos exploran una relación inesperada.'),
        ('The Notebook', 'Nick Cassavetes', 2004, 'Un hombre mayor relata la historia de amor que marcó su juventud.'),
        ('Amelie', 'Jean-Pierre Jeunet', 2001, 'Una joven parisina ayuda discretamente a quienes la rodean mientras busca su propia felicidad.'),
        ('Carol', 'Todd Haynes', 2015, 'Una joven dependienta y una mujer elegante desarrollan un vínculo en la Nueva York de los años cincuenta.'),
        ('Casablanca', 'Michael Curtiz', 1942, 'Un propietario de un café debe decidir qué hacer cuando reaparece un antiguo amor.'),
        ('10 Things I Hate About You', 'Gil Junger', 1999, 'Dos hermanas enfrentan las reglas de su padre y los romances de la escuela.'),
        ('Ghost', 'Jerry Zucker', 1990, 'Un hombre busca proteger a su pareja después de morir en circunstancias misteriosas.'),
        ('The Big Sick', 'Michael Showalter', 2017, 'Una pareja enfrenta diferencias familiares y una crisis de salud inesperada.'),
    ],
    'documental': [
        ('13th', 'Ava DuVernay', 2016, 'Un documental examina la historia de la desigualdad racial y el sistema penitenciario estadounidense.'),
        ('Free Solo', 'Elizabeth Chai Vasarhelyi, Jimmy Chin', 2018, 'El escalador Alex Honnold se prepara para subir una pared de roca sin cuerda.'),
        ('My Octopus Teacher', 'Pippa Ehrlich, James Reed', 2020, 'Un cineasta forma un vínculo inesperado con un pulpo en un bosque submarino.'),
        ('March of the Penguins', 'Luc Jacquet', 2005, 'La película sigue el recorrido anual de los pingüinos emperador para reproducirse.'),
        ('Man on Wire', 'James Marsh', 2008, 'Un documental reconstruye la caminata de Philippe Petit entre las Torres Gemelas.'),
        ('Jiro Dreams of Sushi', 'David Gelb', 2011, 'Un retrato de un maestro del sushi y su búsqueda constante de perfección.'),
        ("Won't You Be My Neighbor?", 'Morgan Neville', 2018, 'La película explora la vida y el legado del presentador Fred Rogers.'),
        ('Icarus', 'Bryan Fogel', 2017, 'Una investigación deportiva descubre un escándalo internacional de dopaje.'),
        ('The Act of Killing', 'Joshua Oppenheimer', 2012, 'Autores de asesinatos masivos recrean sus actos en una película sobre la memoria y la impunidad.'),
        ('Searching for Sugar Man', 'Malik Bendjelloul', 2012, 'Dos admiradores investigan qué ocurrió con un músico cuya obra fue popular lejos de su país.'),
        ('Inside Job', 'Charles Ferguson', 2010, 'Un análisis de las causas y consecuencias de la crisis financiera de 2008.'),
        ('Amy', 'Asif Kapadia', 2015, 'Un documental recorre la vida y la carrera de la cantante Amy Winehouse.'),
    ],
    'animacion': [
        ('Spirited Away', 'Hayao Miyazaki', 2001, 'Chihiro entra en un mundo de espíritus y busca liberar a sus padres.'),
        ('Toy Story', 'John Lasseter', 1995, 'Los juguetes de un niño cobran vida y deben adaptarse a un nuevo compañero.'),
        ('Finding Nemo', 'Andrew Stanton', 2003, 'Un pez payaso cruza el océano para encontrar a su hijo, acompañado por Dory.'),
        ('Coco', 'Lee Unkrich', 2017, 'Miguel visita la Tierra de los Muertos y descubre la historia de su familia.'),
        ('Spider-Man: Into the Spider-Verse', 'Bob Persichetti, Peter Ramsey, Rodney Rothman', 2018, 'Miles Morales conoce a otros Spider-Man de distintas dimensiones.'),
        ('Up', 'Pete Docter', 2009, 'Un viudo y un joven explorador viajan en una casa elevada por globos.'),
        ('Ratatouille', 'Brad Bird', 2007, 'Una rata apasionada por la cocina encuentra una forma insólita de trabajar en París.'),
        ('WALL-E', 'Andrew Stanton', 2008, 'Un pequeño robot recolector encuentra una nueva misión en una Tierra abandonada.'),
        ('Shrek', 'Andrew Adamson, Vicky Jenson', 2001, 'Un ogro emprende una misión para recuperar la tranquilidad de su pantano.'),
        ('How to Train Your Dragon', 'Chris Sanders, Dean DeBlois', 2010, 'Un joven vikingo crea una amistad inesperada con un dragón.'),
        ('The Incredibles', 'Brad Bird', 2004, 'Una familia de superhéroes intenta llevar una vida normal y vuelve a la acción.'),
        ('Inside Out', 'Pete Docter', 2015, 'Las emociones de una niña intentan ayudarla a adaptarse a una nueva ciudad.'),
    ],
    'otros': [
        ('The Prestige', 'Christopher Nolan', 2006, 'Dos ilusionistas rivales llevan su competencia a extremos cada vez más peligrosos.'),
        ('The Artist', 'Michel Hazanavicius', 2011, 'Un actor del cine mudo afronta los cambios que trae la llegada del sonido.'),
        ("The King's Speech", 'Tom Hooper', 2010, 'El futuro rey Jorge VI trabaja con un terapeuta para superar su dificultad al hablar en público.'),
        ('1917', 'Sam Mendes', 2019, 'Dos soldados reciben una misión urgente para evitar una ofensiva durante la Primera Guerra Mundial.'),
        ('The Social Network', 'David Fincher', 2010, 'La creación de una red social provoca conflictos entre sus fundadores.'),
        ('The Wolf of Wall Street', 'Martin Scorsese', 2013, 'Un corredor de bolsa acumula riqueza y excesos mientras crece la investigación en su contra.'),
        ('Birdman', 'Alejandro Gonzalez Inarritu', 2014, 'Un actor prepara una obra teatral mientras intenta redefinir su carrera.'),
        ('The Imitation Game', 'Morten Tyldum', 2014, 'Un equipo de criptoanalistas trabaja para descifrar mensajes durante la Segunda Guerra Mundial.'),
        ('Black Swan', 'Darren Aronofsky', 2010, 'Una bailarina obtiene un papel exigente y comienza a perder la frontera entre realidad y obsesión.'),
        ('Dunkirk', 'Christopher Nolan', 2017, 'Soldados y civiles intentan evacuar a las tropas aliadas cercadas en la costa francesa.'),
        ('The Curious Case of Benjamin Button', 'David Fincher', 2008, 'Un hombre vive el paso del tiempo en sentido inverso y construye una vida extraordinaria.'),
        ('The Green Mile', 'Frank Darabont', 1999, 'Un guardia de prisión conoce a un recluso con un don que desafía su comprensión.'),
    ],
}


def completar_catalogo(apps, schema_editor):
    Pelicula = apps.get_model('peliculas', 'Pelicula')
    peliculas_db = schema_editor.connection.alias

    titulos_existentes = set(
        Pelicula.objects.using(peliculas_db).values_list('titulo', flat=True)
    )
    conteos = {
        fila['genero']: fila['total']
        for fila in Pelicula.objects.using(peliculas_db)
        .values('genero')
        .annotate(total=Count('id'))
    }

    for genero, candidatas in PELICULAS_POR_GENERO.items():
        faltantes = max(12 - conteos.get(genero, 0), 0)
        for titulo, director, anio, sinopsis in candidatas:
            if not faltantes:
                break
            if titulo in titulos_existentes:
                continue
            Pelicula.objects.using(peliculas_db).create(
                titulo=titulo,
                director=director,
                anio_estreno=anio,
                genero=genero,
                sinopsis=sinopsis,
            )
            titulos_existentes.add(titulo)
            faltantes -= 1
        if faltantes:
            raise RuntimeError(f'Faltan películas de respaldo para el género {genero}.')


class Migration(migrations.Migration):
    dependencies = [
        ('peliculas', '0006_actor_director_pelicula_duracion_pelicula_imagen_and_more'),
    ]

    operations = [
        migrations.RunPython(completar_catalogo, migrations.RunPython.noop),
    ]