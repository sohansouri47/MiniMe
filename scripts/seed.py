import asyncio
import httpx
import time
import random
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8001"
USER_EMAIL = "test_user@example.com"

# Categories of journal entries to generate
CATEGORIES = {
    "career": [
        ("Reflecting on System Design Interview prep", 
         "I spent the morning studying system design patterns. Focused on rate limiters, token bucket algorithm, and sharding strategies. I feel confident about the basics, but need to practice drawing diagrams quickly."),
        ("Kubernetes Migration kickoff meeting", 
         "Met with the platform team to discuss our migration to EKS. There is some tension about which ingress controller to use. I proposed using ingress-nginx, but Sarah wants to explore Traefik. We will decide next Tuesday."),
        ("Performance Review feedback", 
         "Received my mid-year review today. My manager praised my technical leadership on the RAG pipeline but noted that I need to delegate more. I tend to hold onto complex tasks instead of coaching junior devs."),
        ("CI/CD pipeline refactoring", 
         "Finally got around to refactoring our GitHub Actions workflow. Reduced build times from 18 minutes to 6 minutes by caching node_modules and docker layers. Small wins feel so satisfying!"),
        ("Frustrations with legacy codebase", 
         "Spent six hours debugging a weird race condition in the legacy auth service. The codebase has no tests and is full of global state. I feel frustrated and want to suggest a complete rewrite."),
        ("Attending tech conference", 
         "Attended the local AWS community day. Met some interesting engineers working on serverless database scaling. The keynote on database-less architectures was provocative but maybe impractical."),
        ("Pair programming with junior engineer", 
         "Spent the afternoon pair programming with Leo. We worked on adding validation schemas using Pydantic. It was rewarding to see him grasp the concept of data validation and dependency injection."),
        ("On-call incident fire", 
         "Got paged at 3 AM. The production database pool was exhausted. It turned out to be a missing close connection call in a new repository class. Fixed it and went back to sleep, but feel exhausted today."),
        ("Salary negotiation prep", 
         "Prepping for my promotion and salary review next week. Gathered all my metrics: 40% reduction in latency, led 3 major releases, mentored 2 juniors. Hopefully, they recognize the impact."),
        ("Writing technical RFC", 
         "Completed the draft RFC for our new event-driven message bus. I'm recommending Apache Kafka over RabbitMQ because of our high retention requirements. Nervous about the review meeting tomorrow.")
    ],
    "fitness": [
        ("Leg day exhaustion", 
         "Did a heavy squats session today. Hit a new personal record of 225 lbs for 5 reps. My legs feel like jelly now. Need to make sure I eat enough protein and drink water tonight."),
        ("Yoga and flexibility training", 
         "Attended a restorative yoga class. My hips and hamstrings are incredibly tight from all the running. The instructor corrected my downward dog. I should do this at least twice a week."),
        ("Macro tracking and meal prep", 
         "Spent Sunday afternoon prepping chicken breast, brown rice, and steamed broccoli. Targeting 150g of protein and 2500 calories per day. It gets boring, but consistency is key for muscle gain."),
        ("New gym membership", 
         "Signed up for a new gym closer to my apartment. It has 4 power racks and a turf area. Training at 6 AM was surprisingly peaceful, and I didn't have to wait for equipment."),
        ("Shoulder pain warning", 
         "Felt a sharp pinch in my left shoulder during overhead press. I immediately stopped the exercise. I think my form was off. I will focus on rotator cuff exercises and rest it for a week."),
        ("High-protein smoothie recipe", 
         "Perfected my post-workout shake: whey protein, banana, peanut butter, almond milk, spinach, and chia seeds. Tastes like a dessert and hits 45g of protein."),
        ("Rest day reflection", 
         "Taking a forced rest day. It is hard for me to sit still, but my body needs recovery. Spent time stretching and using the foam roller while watching a documentary."),
        ("Early morning workout routine", 
         "Woke up at 5:30 AM for a strength session. Core work, deadlifts, and pull-ups. Felt sluggish at first but energized for the rest of the day. Coffee tasted amazing afterwards."),
        ("Body fat percentage progress", 
         "Checked my stats today. Body fat is down to 14.5% while maintaining weight. The slow bulk seems to be working. Need to keep clean eating habits over the weekend."),
        ("Struggling with pull-up targets", 
         "Tried to hit 4 sets of 10 pull-ups but failed on the last set only getting 7 reps. My grip strength is the bottleneck. I will start adding dead hangs to the end of my workouts.")
    ],
    "running": [
        ("Knee pain after long run", 
         "Ran 10 miles this morning. Around mile 8, my left knee started aching on the outer side. I think it might be IT band syndrome again. I need to roll it out, stretch, and maybe take a few days off running."),
        ("Bought new running shoes", 
         "My Brooks Ghost shoes reached 400 miles, so I bought a pair of Saucony Ride today. Took them for a quick 3-mile test run. They feel bouncy and have great arch support."),
        ("Interval training at the track", 
         "Did 6x800m intervals today. Averaged a pace of 3:45 per kilometer. My lungs were burning, but I managed to hit all my target times. Building speed for the upcoming half marathon."),
        ("Rainy day run persistence", 
         "It was pouring rain, but I went out anyway for a 5-mile run. The first mile was miserable, but once I was soaked, it felt liberating. Finished with mud all over my legs."),
        ("Half marathon training plan", 
         "Structured my training plan for the October half marathon. Targeting a sub-1:45 time. That means keeping a consistent 5:00/km pace. Weekly mileage starts at 25 miles and peaks at 40."),
        ("Heart rate zones check", 
         "Did a slow zone 2 recovery run of 4 miles. Kept my heart rate strictly under 140 bpm. It felt painfully slow, but I know building the aerobic base is essential for endurance."),
        ("Early morning trail run", 
         "Ran 6 miles on the forest trail at sunrise. The air was crisp, and the ground was covered in pine needles. Tripped on a root but didn't fall. Trail running is much better for my joints."),
        ("Dehydration warning during hot run", 
         "Ran 8 miles at noon. Temperature was 85 degrees. I didn't bring enough water and felt lightheaded by mile 6. Lesson learned: always carry a handheld flask in summer."),
        ("Pacing improvements", 
         "Ran a tempo 5K today and hit a personal best of 21:40. Felt strong throughout. Pacing was very even, around 4:20/km. All the interval work is starting to pay off."),
        ("Ankle roll recovery", 
         "Slightly rolled my right ankle during a run yesterday. It is a bit swollen today. Putting ice on it and keeping it elevated. Hopefully, it is just a mild sprain and I can run by next week.")
    ],
    "family": [
        ("Sunday family dinner", 
         "Went to my parents' house for Sunday roast. It was great to catch up with my brother. We talked about his new woodworking project. Mom made her classic apple pie."),
        ("Calling parents weekly routine", 
         "Called mom and dad today. They are planning a trip to Florida next month. Dad asked for help setting up his new iPad. It is nice to hear their voices and know they are doing well."),
        ("Sister's birthday celebration", 
         "Celebrated my sister Emma's birthday. We went to a nice Italian restaurant downtown. I got her a cookbook she wanted. She seemed really happy and we laughed about childhood stories."),
        ("Helping dad in the garage", 
         "Spent Saturday helping dad organize his tools and clean the garage. Found some old photo albums from family camping trips in the 90s. We spent an hour just looking through them."),
        ("Planning family holiday gathering", 
         "Had a group call with my siblings to plan Thanksgiving. We decided to host it at my place this year. Feeling a bit anxious about cooking a whole turkey, but excited to host everyone."),
        ("Cousin's wedding announcement", 
         "Received an invitation to my cousin Mark's wedding in Colorado. It will be a destination wedding in the mountains. Looking forward to a mini family reunion next summer."),
        ("Grandmother's health update", 
         "Spoke with my aunt about grandma's health. She is recovering well from her knee surgery and is already walking with a cane. Planning to visit her next weekend to bring her some books."),
        ("Quiet weekend with family", 
         "Spent a relaxed Saturday at home playing board games. We played Settlers of Catan and my sister won by a last-minute route block. Simple weekends like this are the best."),
        ("Debating holiday travel plans", 
         "Having discussions about whether to travel for Christmas. Flights are incredibly expensive, so we might just do a local road trip instead. Need to check hotel availabilities."),
        ("Helping niece with homework", 
         "Helped my 8-year-old niece Lily with her science project on the solar system. We built a papier-mâché model of Saturn. She got so excited about the rings!")
    ],
    "travel": [
        ("Flight delay at JFK", 
         "My flight to London is delayed by 4 hours due to weather. Sitting at JFK airport, drinking overpriced coffee and trying to do some coding. Travel logistics can be exhausting."),
        ("Exploring Tokyo temples", 
         "Spent the day walking around Asakusa and visiting Senso-ji temple in Tokyo. The architecture is stunning. Had amazing ramen for lunch at a tiny 6-seat counter shop."),
        ("Hiking in Switzerland", 
         "Hiked 12 miles in the Lauterbrunnen valley today. The towering waterfalls and snow-capped peaks of the Swiss Alps are breathtaking. My legs are sore but the views were worth it."),
        ("Packing list preparation", 
         "Prepping my bags for a 2-week trip to Japan. Trying to pack light with just a single carry-on backpack. Focused on versatile layers, good walking shoes, and tech adapters."),
        ("Hawaii beach relaxation", 
         "Sitting on the beach in Maui watching the sunset. The water is warm, and the breeze is perfect. Read two chapters of my book. Fully disconnecting from work emails feels wonderful."),
        ("Lost luggage incident", 
         "Arrived in Paris but my suitcase did not. Filed a claim at the airport. Luckily, I packed a change of clothes in my backpack. Hope they locate it within 24 hours."),
        ("Stumbling upon a hidden cafe in Rome", 
         "Got lost in the narrow alleys of Rome and found a charming, vine-covered cafe. Had the best espresso and cannoli of my life. Sometimes getting lost is the best itinerary."),
        ("Train ride through the Japanese countryside", 
         "Riding the Shinkansen from Tokyo to Kyoto. Watching Mt. Fuji pass by in the distance. The train is incredibly quiet, clean, and perfectly on time. Eating a bento box."),
        ("Booking hotels for summer trip", 
         "Spent the evening comparing boutique hotels and Airbnbs in Barcelona. Everything is booking up fast for July. Managed to secure a nice room near the Gothic Quarter."),
        ("Road trip along the Pacific Coast Highway", 
         "Driving down the PCH from San Francisco to Los Angeles. Stopped at Big Sur to look at the coastline. The cliffs dropping into the Pacific Ocean are absolutely spectacular.")
    ],
    "minime": [
        ("Designing the memory indexing system", 
         "Working on the background indexing pipeline for Mini-Me. I need to make sure that when a user saves a journal, the summarization and vector generation happen reliably. Using pgvector for storage."),
        ("Solving the pgvector dimensions mismatch", 
         "Discovered a mismatch in vector dimensions. My SQLAlchemy model was expecting 1536 dimensions, but the embedding model was returning 768. Changed the embedding model to gemini-embedding-2 which supports 1536."),
        ("Prompt engineering for summaries", 
         "Fine-tuning the system prompt for the journal summarization. The summaries were too long and conversational. Rewrote the prompt to enforce a bullet-point style focusing on events and emotions."),
        ("FastAPI async session issues", 
         "Dealt with an async session issue where SQLAlchemy objects became detached after commit. Solved it by calling session.refresh() before returning the validation schema."),
        ("Building the query RAG router", 
         "Implemented the query endpoint. It retrieves the top K matching memories using cosine distance and passes them as context to Gemini. The answers are surprisingly accurate and contextual."),
        ("Rate limit handling with Gemini API", 
         "Implementing backoff logic for external API calls in Mini-Me. The Google API free tier has strict RPM limits. Adding retry decorators to the LLM providers to handle HTTP 429s."),
        ("Drafting the Docker deployment config", 
         "Wrote the Dockerfile and docker-compose.yml for Mini-Me. Running pgvector in a Docker container makes local development extremely easy. Next, need to set up production environment configs."),
        ("Testing the memory clean up deletions", 
         "Added test cases for deleting entries. When a journal entry is deleted, we must also clean up any cached summaries and make sure the vector search space is updated immediately."),
        ("Adding chat history logic", 
         "Started designing the ChatHistory database model. This will store the conversational context of users asking questions about their memories, allowing follow-up questions."),
        ("Refactoring project layout for clean architecture", 
         "Refactoring the Mini-Me src folder. Separated common configuration, databases, and logger from the feature modules (journal and user). This makes the codebase very clean and modular.")
    ]
}

async def seed_data():
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("Starting seed script...")
        
        # Generate 100 entries by cycling through the categories
        entries_to_create = []
        categories_keys = list(CATEGORIES.keys())
        
        # Create 100 entries (each category will get about 16-17 entries)
        for i in range(100):
            cat = categories_keys[i % len(categories_keys)]
            template_list = CATEGORIES[cat]
            # Pick a template based on cycle
            idx = (i // len(categories_keys)) % len(template_list)
            title_base, transcript_base = template_list[idx]
            
            # Add variation to make them unique
            date_offset = 100 - i
            entry_date = (datetime.now() - timedelta(days=date_offset)).strftime("%Y-%m-%d")
            title = f"{title_base} (Day -{date_offset})"
            transcript = f"Entry date: {entry_date}. {transcript_base} (Ref #{i+1})"
            
            entries_to_create.append({
                "user_email": USER_EMAIL,
                "title": title,
                "transcript": transcript
            })
        
        print(f"Generated {len(entries_to_create)} mock entries. Inserting into API...")
        
        inserted_count = 0
        for idx, entry in enumerate(entries_to_create):
            # Implement retry with backoff for rate limits
            backoff = 1.0
            max_retries = 5
            for attempt in range(max_retries):
                try:
                    resp = await client.post(f"{BASE_URL}/api/v1/journal", json=entry)
                    if resp.status_code == 201:
                        inserted_count += 1
                        if inserted_count % 10 == 0:
                            print(f"Progress: {inserted_count}/100 entries successfully indexed.")
                        break
                    elif resp.status_code == 429 or resp.status_code == 500:
                        # Sometimes Gemini API errors present as 500 or 429 when rate limited
                        print(f"Rate limited or server error (status: {resp.status_code}) on entry {idx+1}. Retrying in {backoff}s...")
                        await asyncio.sleep(backoff)
                        backoff *= 2
                    else:
                        print(f"Failed to insert entry {idx+1}: {resp.status_code} - {resp.text}")
                        break
                except Exception as e:
                    print(f"Exception on entry {idx+1}: {str(e)}. Retrying in {backoff}s...")
                    await asyncio.sleep(backoff)
                    backoff *= 2
            
            # Tiny sleep between entries to avoid rate limit spikes
            await asyncio.sleep(4.5)

        print(f"\nSeeding complete! Successfully indexed {inserted_count} out of 100 entries.")

if __name__ == "__main__":
    asyncio.run(seed_data())
