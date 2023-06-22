<h1>Тестовое приложение на FastAPI для работы с Binance</h1>
В приложении есть следующие методы:
<ul>
    <li>Сохранение информации о тикере в бд <code>post: /crypto/create/data</code></li>
    <li>Получение последней цены валюты <code>get: /crypto/ticker/price</code></li>
    <li>Получение получение всех данных по тикеру <code>get: /crypto/all_by_symbol</code></li>
    <li>Создание и запись файла в бд с данными <code>get: /crypto/generate/file</code></li>
    <li>Получение ссылки для скачивания последнего сохраненного файла в бд <code>get: /crypto/download/file</code></li>
 </ul>
