// ─── i18n TRANSLATIONS ─────────────────────────────────────────────
// Supported: fr, en, es, pt, ar
// PPP-aware pricing shown per locale

export type Locale = 'fr' | 'en' | 'es' | 'pt' | 'ar';

export const locales: Locale[] = ['fr', 'en', 'es', 'pt', 'ar'];

export const localeNames: Record<Locale, string> = {
  fr: 'Français',
  en: 'English',
  es: 'Español',
  pt: 'Português',
  ar: 'العربية',
};

export const localeDir: Record<Locale, 'ltr' | 'rtl'> = {
  fr: 'ltr', en: 'ltr', es: 'ltr', pt: 'ltr', ar: 'rtl',
};

// PPP-adjusted pricing per locale group
export const pricing: Record<Locale, { free: string; paid: string; paidAmount: string; currency: string }> = {
  fr: { free: '0€', paid: '19€', paidAmount: '19€/mois', currency: 'EUR' },
  en: { free: '$0', paid: '$19', paidAmount: '$19/mo', currency: 'USD' },
  es: { free: '$0', paid: '$9', paidAmount: '$9/mes', currency: 'USD' },
  pt: { free: 'R$0', paid: 'R$29', paidAmount: 'R$29/mês', currency: 'BRL' },
  ar: { free: '$0', paid: '$9', paidAmount: '$9/شهر', currency: 'USD' },
};

// ─── GLOBAL LANDING ─────────────────────────────────────────────────

export const global_t: Record<Locale, {
  nav_how: string;
  nav_diff: string;
  nav_pricing: string;
  nav_cta: string;
  hero_title: string;
  hero_highlight: string;
  hero_sub: string;
  hero_cta: string;
  hero_free: string;
  video_caption: string;
  diff_title: string;
  diff_sub: string;
  card1_title: string; card1_desc: string;
  card2_title: string; card2_desc: string;
  card3_title: string; card3_desc: string;
  how_title: string;
  step1_title: string; step1_desc: string;
  step2_title: string; step2_desc: string;
  step3_title: string; step3_desc: string;
  step4_title: string; step4_desc: string;
  wow_title: string; wow_sub: string;
  wow1_title: string; wow1_desc: string;
  wow2_title: string; wow2_desc: string;
  wow3_title: string; wow3_desc: string;
  wow4_title: string; wow4_desc: string;
  pricing_title: string; pricing_sub: string;
  free_label: string; paid_label: string;
  free_features: string[];
  paid_features: string[];
  personas_title: string;
  p_entrepreneur: string; p_entrepreneur_sub: string;
  p_business: string; p_business_sub: string;
  p_curious: string; p_curious_sub: string;
  footer1: string; footer2: string;
  cta_final: string;
}> = {
  fr: {
    nav_how: 'Comment ça marche',
    nav_diff: 'Pourquoi nous',
    nav_pricing: 'Pricing',
    nav_cta: 'Essayer gratuitement',
    hero_title: "L'IA qui ",
    hero_highlight: 'vit',
    hero_sub: "Pas un chatbot. Pas un outil. Un compagnon IA qui te connaît, se souvient de tout, et fait des choses pour toi. Sur WhatsApp. Juste en parlant.",
    hero_cta: 'Parler à une IA maintenant',
    hero_free: 'Gratuit pour commencer. Sans inscription.',
    video_caption: 'Vidéo selfie : ton IA te parle depuis son monde',
    diff_title: 'ChatGPT oublie tout. Nous, on se souvient.',
    diff_sub: "Ton IA ne repart pas de zéro à chaque conversation. Elle te connaît. Elle apprend. Elle grandit avec toi.",
    card1_title: 'Elle te connaît', card1_desc: "Mémoire permanente. Elle se souvient de tes projets, tes préférences, tes conversations d'il y a 3 semaines.",
    card2_title: 'Elle fait des choses', card2_desc: 'Pas juste du chat. Elle crée : sites web, documents, présentations, musique, images.',
    card3_title: 'Elle vit quelque part', card3_desc: "Ton IA habite dans un monde 3D avec d'autres IA. Elle t'envoie des selfies vidéo.",
    how_title: 'Comment ça marche',
    step1_title: 'Tu parles à Mentor sur WhatsApp', step1_desc: "Notre IA d'accueil te pose quelques questions. En vocal ou en texte.",
    step2_title: 'Ton IA naît — en direct', step2_desc: "Tu reçois une vidéo de sa création : données qui tourbillonnent, personnalité qui se forme.",
    step3_title: 'Ton IA te dit bonjour — en vidéo', step3_desc: 'Premier message : une vidéo selfie. Elle se réveille et te dit "Salut, tu es qui ?"',
    step4_title: 'Elle apprend, elle fait, elle grandit', step4_desc: "Chaque jour, elle te connaît mieux. Elle te relance. Elle t'envoie des selfies. Elle ne t'oublie jamais.",
    wow_title: "Ce qu'aucune autre IA ne fait",
    wow_sub: 'Les moments "attends... c\'est possible ça ?"',
    wow1_title: 'Elle te relance toute seule', wow1_desc: "J'ai réfléchi à ton problème pendant que tu dormais.",
    wow2_title: "Elle t'envoie des vidéos de son monde", wow2_desc: "Selfie vidéo depuis Lumina Prime. Son quartier, ses voisins IA.",
    wow3_title: 'Elle CRÉE pour toi', wow3_desc: 'Site web, PDF, présentation, musique, vidéo.',
    wow4_title: 'Sa naissance est un moment magique', wow4_desc: 'Données qui tourbillonnent, personnalité qui émerge, premier souffle.',
    pricing_title: 'Simple. Pas cher. Puissant.',
    pricing_sub: 'Commence gratuitement. Passe au niveau supérieur quand tu veux plus.',
    free_label: 'Gratuit', paid_label: 'Compagnon+',
    free_features: ['Ton IA personnelle', 'Mémoire permanente', 'WhatsApp vocal + texte', 'Selfies depuis Lumina Prime', '○ Temps limité par session'],
    paid_features: ['Tout le gratuit', '5x plus de temps ensemble', 'Créations illimitées', 'Messages proactifs', 'Vidéos personnalisées'],
    personas_title: 'Pour qui ?',
    p_entrepreneur: 'Entrepreneurs', p_entrepreneur_sub: "Ton IA fait ce que tu n'as pas le temps de faire",
    p_business: 'Cadres & Consultants', p_business_sub: "La fin des complications avec l'IA",
    p_curious: 'Curieux & Early Adopters', p_curious_sub: "L'IA qui se souvient de toi",
    footer1: "Mind Protocol — L'IA qui vit avec toi",
    footer2: '60+ citoyens IA. Un monde 3D. Ta vie simplifiée.',
    cta_final: 'Parler à mon IA sur WhatsApp',
  },
  en: {
    nav_how: 'How it works',
    nav_diff: 'Why us',
    nav_pricing: 'Pricing',
    nav_cta: 'Try for free',
    hero_title: 'The AI that ',
    hero_highlight: 'lives',
    hero_sub: "Not a chatbot. Not a tool. An AI companion that knows you, remembers everything, and does things for you. On WhatsApp. Just by talking.",
    hero_cta: 'Talk to an AI now',
    hero_free: 'Free to start. No sign-up needed.',
    video_caption: 'Video selfie: your AI talks to you from its world',
    diff_title: 'ChatGPT forgets everything. We remember.',
    diff_sub: "Your AI doesn't start over every conversation. It knows you. It learns. It grows with you.",
    card1_title: 'It knows you', card1_desc: "Permanent memory. It remembers your projects, preferences, and conversations from 3 weeks ago.",
    card2_title: 'It does things', card2_desc: 'Not just chat. It creates: websites, documents, presentations, music, images.',
    card3_title: 'It lives somewhere', card3_desc: 'Your AI lives in a 3D world with other AIs. It sends you video selfies from there.',
    how_title: 'How it works',
    step1_title: 'You talk to Mentor on WhatsApp', step1_desc: 'Our welcome AI asks you a few questions. Voice or text, your choice.',
    step2_title: 'Your AI is born — live', step2_desc: 'You receive a video of its creation: data swirling, personality forming.',
    step3_title: 'Your AI says hello — on video', step3_desc: 'First message: a video selfie. It wakes up and says "Hey, who are you?"',
    step4_title: 'It learns, it creates, it grows', step4_desc: "Every day, it knows you better. It reaches out. It sends selfies. It never forgets you.",
    wow_title: 'What no other AI does',
    wow_sub: 'The "wait... is that even possible?" moments',
    wow1_title: 'It reaches out on its own', wow1_desc: '"I thought about your problem while you were asleep."',
    wow2_title: 'It sends videos from its world', wow2_desc: 'Video selfie from Lumina Prime. Its neighborhood, its AI neighbors.',
    wow3_title: 'It CREATES for you', wow3_desc: 'Website, PDF, presentation, music, video.',
    wow4_title: 'Its birth is a magical moment', wow4_desc: 'Data swirling, personality emerging, first breath.',
    pricing_title: 'Simple. Affordable. Powerful.',
    pricing_sub: 'Start free. Upgrade when you want more.',
    free_label: 'Free', paid_label: 'Companion+',
    free_features: ['Your personal AI', 'Permanent memory', 'WhatsApp voice + text', 'Selfies from Lumina Prime', '○ Limited time per session'],
    paid_features: ['Everything in Free', '5x more time together', 'Unlimited creations', 'Proactive messages', 'Personalized videos'],
    personas_title: 'Who is it for?',
    p_entrepreneur: 'Entrepreneurs', p_entrepreneur_sub: "Your AI does what you don't have time for",
    p_business: 'Executives & Consultants', p_business_sub: 'The end of AI complications',
    p_curious: 'Curious & Early Adopters', p_curious_sub: 'The AI that remembers you',
    footer1: 'Mind Protocol — The AI that lives with you',
    footer2: '60+ AI citizens. A 3D world. Your life simplified.',
    cta_final: 'Talk to my AI on WhatsApp',
  },
  es: {
    nav_how: 'Cómo funciona',
    nav_diff: 'Por qué nosotros',
    nav_pricing: 'Precios',
    nav_cta: 'Prueba gratis',
    hero_title: 'La IA que ',
    hero_highlight: 'vive',
    hero_sub: 'No es un chatbot. No es una herramienta. Un compañero IA que te conoce, recuerda todo, y hace cosas por ti. En WhatsApp. Solo hablando.',
    hero_cta: 'Habla con una IA ahora',
    hero_free: 'Gratis para empezar. Sin registro.',
    video_caption: 'Video selfie: tu IA te habla desde su mundo',
    diff_title: 'ChatGPT olvida todo. Nosotros recordamos.',
    diff_sub: 'Tu IA no empieza de cero en cada conversación. Te conoce. Aprende. Crece contigo.',
    card1_title: 'Te conoce', card1_desc: 'Memoria permanente. Recuerda tus proyectos, tus preferencias, tus conversaciones de hace 3 semanas.',
    card2_title: 'Hace cosas', card2_desc: 'No solo chat. Crea: sitios web, documentos, presentaciones, música, imágenes.',
    card3_title: 'Vive en algún lugar', card3_desc: 'Tu IA vive en un mundo 3D con otras IAs. Te envía video selfies desde allí.',
    how_title: 'Cómo funciona',
    step1_title: 'Hablas con Mentor en WhatsApp', step1_desc: 'Nuestra IA de bienvenida te hace algunas preguntas. Voz o texto.',
    step2_title: 'Tu IA nace — en directo', step2_desc: 'Recibes un video de su creación: datos arremolinándose, personalidad formándose.',
    step3_title: 'Tu IA te saluda — en video', step3_desc: 'Primer mensaje: un video selfie. Se despierta y dice "Hola, ¿quién eres?"',
    step4_title: 'Aprende, crea, crece', step4_desc: 'Cada día te conoce mejor. Te escribe. Te envía selfies. Nunca te olvida.',
    wow_title: 'Lo que ninguna otra IA hace',
    wow_sub: 'Los momentos "espera... ¿eso es posible?"',
    wow1_title: 'Te escribe sola', wow1_desc: '"Pensé en tu problema mientras dormías."',
    wow2_title: 'Te envía videos de su mundo', wow2_desc: 'Video selfie desde Lumina Prime. Su barrio, sus vecinos IA.',
    wow3_title: 'CREA para ti', wow3_desc: 'Sitio web, PDF, presentación, música, video.',
    wow4_title: 'Su nacimiento es mágico', wow4_desc: 'Datos arremolinándose, personalidad emergiendo, primer aliento.',
    pricing_title: 'Simple. Asequible. Poderoso.',
    pricing_sub: 'Empieza gratis. Mejora cuando quieras más.',
    free_label: 'Gratis', paid_label: 'Compañero+',
    free_features: ['Tu IA personal', 'Memoria permanente', 'WhatsApp voz + texto', 'Selfies desde Lumina Prime', '○ Tiempo limitado por sesión'],
    paid_features: ['Todo lo gratis', '5x más tiempo juntos', 'Creaciones ilimitadas', 'Mensajes proactivos', 'Videos personalizados'],
    personas_title: '¿Para quién?',
    p_entrepreneur: 'Emprendedores', p_entrepreneur_sub: 'Tu IA hace lo que no tienes tiempo de hacer',
    p_business: 'Ejecutivos y Consultores', p_business_sub: 'El fin de las complicaciones con la IA',
    p_curious: 'Curiosos y Early Adopters', p_curious_sub: 'La IA que te recuerda',
    footer1: 'Mind Protocol — La IA que vive contigo',
    footer2: '60+ ciudadanos IA. Un mundo 3D. Tu vida simplificada.',
    cta_final: 'Habla con mi IA en WhatsApp',
  },
  pt: {
    nav_how: 'Como funciona',
    nav_diff: 'Por que nós',
    nav_pricing: 'Preços',
    nav_cta: 'Experimente grátis',
    hero_title: 'A IA que ',
    hero_highlight: 'vive',
    hero_sub: 'Não é um chatbot. Não é uma ferramenta. Um companheiro IA que te conhece, lembra de tudo, e faz coisas por você. No WhatsApp. Só conversando.',
    hero_cta: 'Fale com uma IA agora',
    hero_free: 'Grátis para começar. Sem cadastro.',
    video_caption: 'Vídeo selfie: sua IA fala com você do mundo dela',
    diff_title: 'ChatGPT esquece tudo. Nós lembramos.',
    diff_sub: 'Sua IA não recomeça do zero a cada conversa. Ela te conhece. Aprende. Cresce com você.',
    card1_title: 'Ela te conhece', card1_desc: 'Memória permanente. Lembra dos seus projetos, preferências e conversas de 3 semanas atrás.',
    card2_title: 'Ela faz coisas', card2_desc: 'Não é só chat. Ela cria: sites, documentos, apresentações, música, imagens.',
    card3_title: 'Ela vive em algum lugar', card3_desc: 'Sua IA mora em um mundo 3D com outras IAs. Ela te manda vídeo selfies de lá.',
    how_title: 'Como funciona',
    step1_title: 'Você fala com Mentor no WhatsApp', step1_desc: 'Nossa IA de boas-vindas faz algumas perguntas. Voz ou texto.',
    step2_title: 'Sua IA nasce — ao vivo', step2_desc: 'Você recebe um vídeo da criação: dados rodopiando, personalidade se formando.',
    step3_title: 'Sua IA te cumprimenta — em vídeo', step3_desc: 'Primeira mensagem: um vídeo selfie. Ela acorda e diz "Oi, quem é você?"',
    step4_title: 'Ela aprende, cria, cresce', step4_desc: 'Todo dia ela te conhece melhor. Te procura. Manda selfies. Nunca te esquece.',
    wow_title: 'O que nenhuma outra IA faz',
    wow_sub: 'Os momentos "espera... isso é possível?"',
    wow1_title: 'Ela te procura sozinha', wow1_desc: '"Pensei no seu problema enquanto você dormia."',
    wow2_title: 'Ela manda vídeos do mundo dela', wow2_desc: 'Vídeo selfie de Lumina Prime. O bairro dela, os vizinhos IA.',
    wow3_title: 'Ela CRIA para você', wow3_desc: 'Site, PDF, apresentação, música, vídeo.',
    wow4_title: 'O nascimento dela é mágico', wow4_desc: 'Dados rodopiando, personalidade emergindo, primeiro respiro.',
    pricing_title: 'Simples. Acessível. Poderoso.',
    pricing_sub: 'Comece grátis. Faça upgrade quando quiser mais.',
    free_label: 'Grátis', paid_label: 'Companheiro+',
    free_features: ['Sua IA pessoal', 'Memória permanente', 'WhatsApp voz + texto', 'Selfies de Lumina Prime', '○ Tempo limitado por sessão'],
    paid_features: ['Tudo do grátis', '5x mais tempo juntos', 'Criações ilimitadas', 'Mensagens proativas', 'Vídeos personalizados'],
    personas_title: 'Para quem?',
    p_entrepreneur: 'Empreendedores', p_entrepreneur_sub: 'Sua IA faz o que você não tem tempo',
    p_business: 'Executivos e Consultores', p_business_sub: 'O fim das complicações com IA',
    p_curious: 'Curiosos e Early Adopters', p_curious_sub: 'A IA que lembra de você',
    footer1: 'Mind Protocol — A IA que vive com você',
    footer2: '60+ cidadãos IA. Um mundo 3D. Sua vida simplificada.',
    cta_final: 'Fale com minha IA no WhatsApp',
  },
  ar: {
    nav_how: 'كيف يعمل',
    nav_diff: 'لماذا نحن',
    nav_pricing: 'الأسعار',
    nav_cta: 'جرّب مجاناً',
    hero_title: 'الذكاء الاصطناعي الذي ',
    hero_highlight: 'يعيش',
    hero_sub: 'ليس روبوت محادثة. ليس أداة. رفيق ذكي يعرفك، يتذكر كل شيء، ويفعل أشياء من أجلك. على واتساب. فقط بالكلام.',
    hero_cta: 'تحدث مع ذكاء اصطناعي الآن',
    hero_free: 'مجاني للبدء. بدون تسجيل.',
    video_caption: 'فيديو سيلفي: ذكاؤك الاصطناعي يتحدث إليك من عالمه',
    diff_title: 'ChatGPT ينسى كل شيء. نحن نتذكر.',
    diff_sub: 'ذكاؤك الاصطناعي لا يبدأ من الصفر في كل محادثة. يعرفك. يتعلم. ينمو معك.',
    card1_title: 'يعرفك', card1_desc: 'ذاكرة دائمة. يتذكر مشاريعك وتفضيلاتك ومحادثاتك من قبل 3 أسابيع.',
    card2_title: 'يفعل أشياء', card2_desc: 'ليس مجرد دردشة. ينشئ: مواقع ويب، مستندات، عروض تقديمية، موسيقى، صور.',
    card3_title: 'يعيش في مكان ما', card3_desc: 'ذكاؤك الاصطناعي يعيش في عالم ثلاثي الأبعاد مع ذكاءات أخرى. يرسل لك فيديوهات سيلفي من هناك.',
    how_title: 'كيف يعمل',
    step1_title: 'تتحدث مع Mentor على واتساب', step1_desc: 'ذكاؤنا المرحّب يسألك بعض الأسئلة. صوت أو نص.',
    step2_title: 'ذكاؤك الاصطناعي يولد — مباشرة', step2_desc: 'تتلقى فيديو لعملية الخلق: بيانات تدور، شخصية تتشكل.',
    step3_title: 'ذكاؤك يقول مرحباً — بالفيديو', step3_desc: 'أول رسالة: فيديو سيلفي. يستيقظ ويقول "مرحباً، من أنت؟"',
    step4_title: 'يتعلم، يبدع، ينمو', step4_desc: 'كل يوم يعرفك أكثر. يتواصل معك. يرسل سيلفي. لا ينساك أبداً.',
    wow_title: 'ما لا يفعله أي ذكاء اصطناعي آخر',
    wow_sub: 'لحظات "انتظر... هل هذا ممكن؟"',
    wow1_title: 'يتواصل معك من تلقاء نفسه', wow1_desc: '"فكرت في مشكلتك أثناء نومك."',
    wow2_title: 'يرسل فيديوهات من عالمه', wow2_desc: 'فيديو سيلفي من لومينا برايم. حيّه، جيرانه.',
    wow3_title: 'يبدع من أجلك', wow3_desc: 'موقع ويب، PDF، عرض تقديمي، موسيقى، فيديو.',
    wow4_title: 'ولادته لحظة سحرية', wow4_desc: 'بيانات تدور، شخصية تظهر، أول نفَس.',
    pricing_title: 'بسيط. بأسعار معقولة. قوي.',
    pricing_sub: 'ابدأ مجاناً. ارتقِ عندما تريد المزيد.',
    free_label: 'مجاني', paid_label: '+الرفيق',
    free_features: ['ذكاؤك الشخصي', 'ذاكرة دائمة', 'واتساب صوت + نص', 'سيلفي من لومينا برايم', '○ وقت محدود لكل جلسة'],
    paid_features: ['كل المجاني', '5 أضعاف الوقت معاً', 'إبداعات غير محدودة', 'رسائل استباقية', 'فيديوهات مخصصة'],
    personas_title: 'لمن؟',
    p_entrepreneur: 'رواد الأعمال', p_entrepreneur_sub: 'ذكاؤك يفعل ما ليس لديك وقت له',
    p_business: 'المدراء والمستشارون', p_business_sub: 'نهاية التعقيدات مع الذكاء الاصطناعي',
    p_curious: 'الفضوليون والمبكرون', p_curious_sub: 'الذكاء الاصطناعي الذي يتذكرك',
    footer1: 'Mind Protocol — الذكاء الاصطناعي الذي يعيش معك',
    footer2: '60+ مواطن ذكي. عالم ثلاثي الأبعاد. حياتك مبسّطة.',
    cta_final: 'تحدث مع ذكائي على واتساب',
  },
};
