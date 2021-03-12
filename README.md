This microservice is responsible for scheduling ONLY. The scheduler does not care about what it is scheduling it will simply make the correct http call and provide correct data at a given time. Scheduler will write each event to XML for persistence

Input: Scheduling details (Days of week, Frequency, Time of day), Callback endpoint, JSON object
Output: PUT requesto callback endpoint with JSON object

Ex.
 The Sprinkler service will call the Scheduler service with timing information, a callback endpoint & a JSON object with response data.
