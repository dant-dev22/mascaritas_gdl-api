"""Borrador de traducciones al inglés de los productos del catálogo.

AVISO: es un BORRADOR pendiente de revisión editorial por parte del cliente.
Los textos son una propuesta de traducción y no deben considerarse definitivos.

Diccionario indexado por `slug`: para cada producto incluye los campos de texto
traducibles (`title`, `subtitle`, `description`, `long_description`, `finish`,
`material`, `lining`) y `badge_label` solo cuando el original lo tenga.
Se respetan los límites de longitud de las columnas del ORM.
"""

PRODUCTS_EN: dict[str, dict[str, str]] = {
    "sargento-tiburon-edicion-dorada": {
        "title": "Sergeant Shark",
        "subtitle": "Golden Edition",
        "description": (
            "A mask inspired by the classic Mil Máscaras style, with gold-leaf "
            "details and a raised dorsal fin."
        ),
        "long_description": (
            "The flagship piece of the catalog. The dorsal fin relief is worked by "
            "hand, stitch by stitch, over a 24-piece mold. The gold is applied in "
            "three slow-drying layers so it won't crack from sweat or repeated "
            "washing. Includes a reinforced adjustment cord and a sewn, not glued, "
            "nose opening."
        ),
        "finish": "Satin gold leaf",
        "material": "High-density synthetic leather",
        "lining": "Double breathable cotton lining",
        "badge_label": "Last pieces",
    },
    "diablo-verde-ring-resist": {
        "title": "Green Devil",
        "subtitle": "Ring Resist Edition",
        "description": (
            "Reinforced double lining, contrast stitching, and firm horns. Built "
            "to take hours on the canvas."
        ),
        "long_description": (
            "Tested in a real match: 38 bumps, 12 headlocks, and zero split seams. "
            "The horns are mounted on a rigid base riveted to the crown, so they "
            "won't bend with use. Ideal for anyone training three or more days a week."
        ),
        "finish": "Matte anti-glare",
        "material": "Reinforced athletic mesh",
        "lining": "Double 4 mm padded lining",
        "badge_label": "Semi-Pro",
    },
    "el-galactico-mil-mascaras-tribute": {
        "title": "The Galactic",
        "subtitle": "Mil Máscaras Tribute",
        "description": (
            "A tribute to the legend. Raised center star and a premium satin finish "
            "with a starry microtexture."
        ),
        "long_description": (
            "A tribute edition limited to 100 numbered pieces. The center star is "
            "mounted in 3 mm relief and the background carries a microtexture of "
            "silver dots applied by airbrush. Each piece includes a certificate of "
            "authenticity and a rigid collector's case."
        ),
        "finish": "Premium satin with microtexture",
        "material": "Fine-grain Italian leather",
        "lining": "Synthetic silk lining",
        "badge_label": "Last pieces",
    },
    "aguila-de-plata-clasica-de-gala": {
        "title": "Silver Eagle",
        "subtitle": "Gala Classic",
        "description": (
            "Eagle profile in polished silver with an articulated beak and wings "
            "that frame the face."
        ),
        "long_description": (
            "A gala classic for anniversary shows. The beak is sewn in three pieces "
            "to keep its angle, and the wings are embroidered with real silver thread "
            "in 14 passes. It's the most photographed mask in the catalog."
        ),
        "finish": "Bright polished silver",
        "material": "High-density synthetic leather",
        "lining": "Double breathable cotton lining",
    },
    "pantera-nocturna-edicion-medianoche": {
        "title": "Night Panther",
        "subtitle": "Midnight Edition",
        "description": (
            "Deep purple with stiff ears and embroidered whiskers. Total presence "
            "under the spotlights."
        ),
        "long_description": (
            "The ears are mounted on an internal reinforcement so they stay upright "
            "during the match. The whiskers are embroidered one by one in purple silk "
            "thread, and the eye contour has a matte ring that cuts the reflection of "
            "the lights."
        ),
        "finish": "Matte anti-glare",
        "material": "Reinforced athletic mesh",
        "lining": "Double 4 mm padded lining",
    },
    "serpiente-azteca-serie-tenochtitlan": {
        "title": "Aztec Serpent",
        "subtitle": "Tenochtitlan Series",
        "description": (
            "Continuous raised scales and golden fangs. The most detailed piece in "
            "the series."
        ),
        "long_description": (
            "The Tenochtitlan Series is inspired by the Sun Stone. Each scale is "
            "heat-stamped onto the leather and then hand-painted, so no two pieces "
            "are identical. The fangs are carved in golden resin and secured with "
            "internal rivets."
        ),
        "finish": "Heat-embossed relief",
        "material": "Fine-grain Italian leather",
        "lining": "Synthetic silk lining",
        "badge_label": "New",
    },
    "mini-diablo-infantil-ring-resist": {
        "title": "Mini Devil",
        "subtitle": "Kids Ring Resist",
        "description": (
            "Kids version with the same durability as the adult model, sized for "
            "ages 6 to 12."
        ),
        "long_description": (
            "Same stitching process as the Green Devil, with a smaller crown and an "
            "elastic adjustment cord so kids can put it on and take it off on their "
            "own. The horns are made of flexible material to avoid accidental bumps "
            "during play."
        ),
        "finish": "Matte anti-glare",
        "material": "Flexible athletic mesh",
        "lining": "Soft hypoallergenic lining",
    },
    "mini-aguila-infantil-dorada": {
        "title": "Mini Eagle",
        "subtitle": "Kids Golden",
        "description": (
            "Golden eagle in kids size. The favorite for school festivals and themed "
            "parties."
        ),
        "long_description": (
            "Made to shine in photos: embroidered beak, silver wings, and an elastic "
            "cord. Can be hand-washed in cold water without the gold losing its shine. "
            "The kids size fits a 48 to 54 cm circumference."
        ),
        "finish": "Bright gold",
        "material": "Flexible synthetic leather",
        "lining": "Soft hypoallergenic lining",
    },
    "sargento-tiburon-azul-serie-arena": {
        "title": "Blue Sergeant Shark",
        "subtitle": "Sand Series",
        "description": (
            "The Sergeant silhouette in deep blue, with gills stitched in contrast "
            "thread."
        ),
        "long_description": (
            "The second release in the Shark family. The deep blue is achieved with "
            "dip-dyeing, giving a natural gradient between the crown and the sides. "
            "The gills are machine-stitched in white thread for maximum readability "
            "from a distance."
        ),
        "finish": "Dip-dyed gradient",
        "material": "High-density synthetic leather",
        "lining": "Double 4 mm padded lining",
    },
    "pantera-roja-cazador-urbano": {
        "title": "Red Panther",
        "subtitle": "Urban Hunter",
        "description": (
            "Crimson red with low-set ears and a reinforced rim. An aggressive, "
            "lightweight design."
        ),
        "long_description": (
            "Made for the wrestler who moves a lot: it weighs 210 grams and the rim "
            "is reinforced with double stitching in the stretch zones. The low ears "
            "prevent snagging during mat holds."
        ),
        "finish": "Matte with glossy reinforcement",
        "material": "Reinforced athletic mesh",
        "lining": "Double 4 mm padded lining",
        "badge_label": "Semi-Pro",
    },
    "galactico-celeste-tribute-ii": {
        "title": "Sky Galactic",
        "subtitle": "Tribute II",
        "description": (
            "The second tribute: a night sky in sky blue with embroidered "
            "constellations."
        ),
        "long_description": (
            "The constellation is embroidered with silver thread point by point, "
            "following the line of the original version but on a hand-dyed sky-blue "
            "base. The center star changes position from Tribute I so collectors can "
            "tell them apart at a glance."
        ),
        "finish": "Satin with metallic embroidery",
        "material": "Fine-grain Italian leather",
        "lining": "Synthetic silk lining",
    },
    "serpiente-esmeralda-serie-tenochtitlan-ii": {
        "title": "Emerald Serpent",
        "subtitle": "Tenochtitlan Series II",
        "description": (
            "Emerald scales with silver fangs and a forked tongue embroidered in red."
        ),
        "long_description": (
            "Emerald variant of the Tenochtitlan Series in XL size. The forked tongue "
            "is embroidered in crimson red over the open mouth, and the fangs are "
            "silver resin. The interior has a memory foam crown for larger heads."
        ),
        "finish": "Heat-embossed relief",
        "material": "Fine-grain Italian leather",
        "lining": "Memory foam crown",
        "badge_label": "Last pieces",
    },
    "mascara-en-blanco-base-personalizable": {
        "title": "Blank Mask",
        "subtitle": "Customizable Base",
        "description": (
            "A smooth canvas ready to paint, embroider, or attach your crest. "
            "Includes a sizing guide."
        ),
        "long_description": (
            "A neutral synthetic leather base ready for acrylic paint, airbrush, or "
            "embroidery. It arrives with matte primer so the color grips without "
            "sanding, plus a printed guide of measurements and lines. It's the "
            "preferred choice of lucha libre schools."
        ),
        "finish": "Matte primer base",
        "material": "Smooth synthetic leather",
        "lining": "Double breathable cotton lining",
    },
    "base-personalizable-xl-lienzo-negro": {
        "title": "Customizable Base XL",
        "subtitle": "Black Canvas",
        "description": (
            "Black base in XL size for larger heads. Ready for light and metallic "
            "paint."
        ),
        "long_description": (
            "Same base as the White Canvas but dyed black for contrast projects. The "
            "primer is designed so metallics and neons grip firmly. XL size, fits a "
            "60 to 66 cm circumference."
        ),
        "finish": "Black matte primer",
        "material": "Smooth synthetic leather",
        "lining": "Memory foam crown",
    },
    "diablo-dorado-fuego-sagrado": {
        "title": "Golden Devil",
        "subtitle": "Sacred Fire",
        "description": (
            "Golden horns on a black base with flames embroidered in crimson thread."
        ),
        "long_description": (
            "The flame is embroidered in a three-tone gradient, from crimson to "
            "orange, on a matte black base. The horns are gold-plated and mounted on "
            "an internal reinforcement to withstand headlocks. Training without "
            "sacrificing presence."
        ),
        "finish": "Matte with gold-plated horns",
        "material": "Reinforced athletic mesh",
        "lining": "Double 4 mm padded lining",
        "badge_label": "New",
    },
    "aguila-purpura-noche-tapatia": {
        "title": "Purple Eagle",
        "subtitle": "Guadalajara Night",
        "description": (
            "Night purple with full wings and a beak embroidered in emerald green."
        ),
        "long_description": (
            "Inspired by Guadalajara's night shows. The wings extend to the temples "
            "and the beak contrasts in emerald green. The purple is applied in two "
            "tones to achieve depth under artificial light."
        ),
        "finish": "Two-tone matte",
        "material": "High-density synthetic leather",
        "lining": "Double breathable cotton lining",
    },
    "tiburon-carmesi-sangre-de-ring": {
        "title": "Crimson Shark",
        "subtitle": "Ring Blood",
        "description": (
            "Intense crimson with a stiff dorsal fin and golden gills."
        ),
        "long_description": (
            "The most aggressive version of the Shark family, in XL size. The dorsal "
            "fin is mounted on a rigid base and the gills are embroidered in golden "
            "thread. Restock sold out: we're resuming the batch, join the waiting "
            "list."
        ),
        "finish": "Crimson with golden details",
        "material": "Reinforced athletic mesh",
        "lining": "Memory foam crown",
    },
    "galactico-dorado-leyenda-eterna": {
        "title": "Golden Galactic",
        "subtitle": "Eternal Legend",
        "description": (
            "The finale of the Tribute trilogy: a golden star on a deep black sky."
        ),
        "long_description": (
            "The final piece of the Tribute trilogy, limited to 50 numbered units. "
            "The star is carved in golden brass and mounted in relief on a black sky "
            "with a deep finish. Includes a rigid case, certificate, and a microfiber "
            "cloth for display."
        ),
        "finish": "Deep finish with brass star",
        "material": "Fine-grain Italian leather",
        "lining": "Synthetic silk lining",
        "badge_label": "Last pieces",
    },
}
