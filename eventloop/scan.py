import vk_api
from time import strftime, localtime, sleep
from datetime import timedelta
from queue import Queue
from glue.models import Community
import threading
from celery.decorators import periodic_task

LIMIT = 5

@periodic_task(run_every=timedelta(seconds=15))
def start_workers():
    num_fetch_threads = 1
    fetch_queue = Queue()

    workers = []

    for community in Community.objects.all():
        fetch_queue.put(community)

    for i in range(num_fetch_threads):
        worker = threading.Thread(
            target=scan_wall,
            args=(fetch_queue,),
            name='worker-{}'.format(i),
        )
        worker.setDaemon(True)
        worker.start()
        workers.append(worker)


    for worker in workers:
        worker.join()

def scan_wall(queue):
    session = vk_api.VkApi()
    api = session.get_api()
    while not queue.empty():
        community = queue.get()
        url = community.vk_domen
       
        response = api.wall.get(owner_id=-url, extended=1, count=LIMIT)
        posts = list(community.post_set.all())
        name = response['groups'][0]['name']
        print(len(response['items']))
        for i in range(0, len(response['items'])):
            try:
                text = response['items'][i]['text']
                for post in posts:
                    if text == post.text:
                        post_id = response['items'][i]['id']
                        post.is_posted = True
                        post.vk_id_real = post_id
                        post.save()

            except TypeError:
                print ('TypeError')
                return
        print("posts in response: %s, posts in db: %s" % (len(response), len(posts)))
