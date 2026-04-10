const places = [
  {
    name: 'Ласточкино гнездо',
    tags: ['castle', 'sea', 'view'],
    info: 'Знаковый замок на отвесной скале у моря.',
    wikiQuery: 'Swallow Nest Crimea',
  },
  {
    name: 'Балаклава',
    tags: ['bay', 'boats', 'sunset'],
    info: 'Живописная бухта с набережной и морской атмосферой.',
    wikiQuery: 'Balaklava bay Crimea',
  },
  {
    name: 'Херсонес Таврический',
    tags: ['ruins', 'history', 'columns'],
    info: 'Античные руины и исторический центр рядом с морем.',
    wikiQuery: 'Chersonesus Crimea',
  },
  {
    name: 'Ай-Петри',
    tags: ['mountains', 'clouds', 'cablecar'],
    info: 'Горные виды, прохлада и панорамы южного берега.',
    wikiQuery: 'Ai-Petri Crimea',
  },
  {
    name: 'Новый Свет',
    tags: ['trail', 'cliffs', 'water'],
    info: 'Тропа Голицына, изумрудная вода и скальные бухты.',
    wikiQuery: 'Novyi Svet Crimea',
  },
  {
    name: 'Судак и Генуэзская крепость',
    tags: ['fortress', 'panorama', 'ancient'],
    info: 'Средневековая крепость и яркие исторические виды.',
    wikiQuery: 'Genoese Fortress Sudak',
  },
  {
    name: 'Форосская церковь',
    tags: ['church', 'cliff', 'landscape'],
    info: 'Церковь на скале с впечатляющей панорамой побережья.',
    wikiQuery: 'Foros Church Crimea',
  },
  {
    name: 'Тарханкут',
    tags: ['cape', 'rocks', 'clearwater'],
    info: 'Чистейшее море, арки из камня и дикая красота природы.',
    wikiQuery: 'Cape Tarkhankut Crimea',
  },
];

const tones = {
  inspiring: 'Ощутите настроение путешествия и вдохновения',
  informative: 'Коротко расскажите факты и пользу для туриста',
  promo: 'Подчеркните привлекательность места и призыв к поездке',
};

const startDateInput = document.querySelector('#startDate');
const endDateInput = document.querySelector('#endDate');
const themeInput = document.querySelector('#theme');
const generateBtn = document.querySelector('#generateBtn');
const generate100Btn = document.querySelector('#generate100Btn');
const postsContainer = document.querySelector('#postsContainer');
const summaryBlock = document.querySelector('#summary');
const actionsBlock = document.querySelector('#actions');
const downloadJsonBtn = document.querySelector('#downloadJsonBtn');
const downloadCsvBtn = document.querySelector('#downloadCsvBtn');
const postCardTemplate = document.querySelector('#postCardTemplate');

let generatedPosts = [];
const photoCache = new Map();

generateBtn.addEventListener('click', async () => {
  const startDate = new Date(startDateInput.value);
  const endDate = new Date(endDateInput.value);

  if (!validateDates(startDate, endDate)) {
    return;
  }

  await runGeneration(startDate, endDate, themeInput.value);
});

generate100Btn.addEventListener('click', async () => {
  const startDate = new Date(startDateInput.value);

  if (Number.isNaN(startDate.getTime())) {
    alert('Заполните корректную дату начала.');
    return;
  }

  const endDate = new Date(startDate);
  endDate.setDate(endDate.getDate() + 99);
  endDateInput.value = toInputDate(endDate);

  await runGeneration(startDate, endDate, themeInput.value);
});

downloadJsonBtn.addEventListener('click', () => {
  downloadFile(
    JSON.stringify(generatedPosts, null, 2),
    'crimea_posts_plan.json',
    'application/json'
  );
});

downloadCsvBtn.addEventListener('click', () => {
  const rows = [
    ['date', 'place', 'title', 'description', 'photo_1', 'photo_2', 'photo_3'],
    ...generatedPosts.map((post) => [
      post.date,
      post.place,
      post.title,
      post.description,
      post.photos[0],
      post.photos[1],
      post.photos[2],
    ]),
  ];

  const csv = rows
    .map((row) => row.map((item) => `"${String(item).replaceAll('"', '""')}"`).join(','))
    .join('\n');

  downloadFile(csv, 'crimea_posts_plan.csv', 'text/csv;charset=utf-8;');
});

async function runGeneration(startDate, endDate, toneKey) {
  toggleLoading(true);

  try {
    generatedPosts = await buildPosts(startDate, endDate, toneKey);
    renderSummary(generatedPosts, startDate, endDate);
    renderPosts(generatedPosts);
    actionsBlock.hidden = false;
  } catch (error) {
    alert(`Ошибка генерации: ${error.message}`);
  } finally {
    toggleLoading(false);
  }
}

function validateDates(startDate, endDate) {
  if (Number.isNaN(startDate.getTime()) || Number.isNaN(endDate.getTime())) {
    alert('Пожалуйста, заполните даты корректно.');
    return false;
  }

  if (startDate > endDate) {
    alert('Дата начала должна быть раньше или равна дате окончания.');
    return false;
  }

  return true;
}

async function buildPosts(startDate, endDate, toneKey) {
  const posts = [];
  const cursor = new Date(startDate);
  let index = 0;

  while (cursor <= endDate) {
    const place = places[index % places.length];
    const dateStr = formatDate(cursor);
    const photos = await findThreePhotos(place);

    posts.push({
      date: dateStr,
      place: place.name,
      title: `${dateStr} — ${place.name}`,
      description: `${tones[toneKey]}. ${place.info} Идея поста: покажите атмосферу локации и добавьте мини-маршрут на день.`,
      photos,
    });

    index += 1;
    cursor.setDate(cursor.getDate() + 1);
  }

  return posts;
}

async function findThreePhotos(place) {
  if (photoCache.has(place.name)) {
    return photoCache.get(place.name);
  }

  const url = new URL('https://commons.wikimedia.org/w/api.php');
  url.search = new URLSearchParams({
    action: 'query',
    format: 'json',
    generator: 'search',
    gsrsearch: place.wikiQuery,
    gsrnamespace: '6',
    gsrlimit: '12',
    prop: 'imageinfo',
    iiprop: 'url',
    origin: '*',
  }).toString();

  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`не удалось получить фото (${response.status})`);
  }

  const data = await response.json();
  const pages = Object.values(data?.query?.pages || {});

  const photos = pages
    .map((page) => page.imageinfo?.[0]?.url)
    .filter(Boolean)
    .slice(0, 3);

  if (photos.length < 3) {
    const fallback = place.tags.map(
      (tag, idx) => `https://picsum.photos/seed/${encodeURIComponent(place.name)}-${tag}-${idx}/1200/800`
    );
    photoCache.set(place.name, fallback);
    return fallback;
  }

  photoCache.set(place.name, photos);
  return photos;
}

function renderSummary(posts, startDate, endDate) {
  summaryBlock.hidden = false;
  summaryBlock.innerHTML = `
    <strong>Готово: ${posts.length} постов</strong>
    <span>Период: ${formatDate(startDate)} — ${formatDate(endDate)}</span>
    <span>Формат: 1 пост на дату, 3 фото + описание</span>
  `;
}

function renderPosts(posts) {
  postsContainer.innerHTML = '';

  posts.forEach((post) => {
    const card = postCardTemplate.content.cloneNode(true);

    card.querySelector('.post-title').textContent = post.title;
    card.querySelector('.post-place').textContent = post.place;
    card.querySelector('.post-description').textContent = post.description;

    const photoGrid = card.querySelector('.photo-grid');
    post.photos.forEach((photo, index) => {
      const link = document.createElement('a');
      link.href = photo;
      link.target = '_blank';
      link.rel = 'noopener noreferrer';

      const img = document.createElement('img');
      img.loading = 'lazy';
      img.alt = `${post.place} фото ${index + 1}`;
      img.src = photo;

      link.appendChild(img);
      photoGrid.appendChild(link);
    });

    postsContainer.appendChild(card);
  });
}

function formatDate(date) {
  const day = String(date.getDate()).padStart(2, '0');
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const year = date.getFullYear();
  return `${day}.${month}.${year}`;
}

function toInputDate(date) {
  const day = String(date.getDate()).padStart(2, '0');
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const year = date.getFullYear();
  return `${year}-${month}-${day}`;
}

function toggleLoading(isLoading) {
  generateBtn.disabled = isLoading;
  generate100Btn.disabled = isLoading;
  generateBtn.textContent = isLoading ? 'Идёт генерация…' : 'Сгенерировать по диапазону';
}

function downloadFile(content, fileName, mimeType) {
  if (!generatedPosts.length) {
    alert('Сначала сгенерируйте посты.');
    return;
  }

  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = fileName;
  link.click();
  URL.revokeObjectURL(url);
}
