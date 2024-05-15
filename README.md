# Web Crawler Project

## Introduction
This project develops a simple web crawler capable of downloading all pages from a specific entry point to a local storage system using multithreading.
This README.md file provides Guidelines for current implementation as well as ideas for a Sytem Design and further enhancements to improve the system.

## Task Clarifications
- **Single Entry**: The system currently supports a single entry point per crawling session.
- **Download Once**: We need to download each page only once.
- **Local Storage**: Data is stored locally.
- **Loops**: Provide basic solution for avoiding loops.
- **Multiple URL pointers**: multiple URLs can point to same Page.
- **Completion Indication**: create a basic mechanism for indication of succesful completion.
- **Efficiency**: as much as possible.

## Running instructions

### Prerequisites
**Python**: Ensure Python 3.6+ is installed on your system. [Download Python](https://www.python.org/downloads/)
    
### Running the Crawler
Navigate to the project directory and run the crawler using:
```bash
cd myWebCrawler
```
Run the program - it will ask you to provide base url
for example:
```bash
https://webscraper.io/test-sites/e-commerce/allinone
```
**Output** - crawled.txt file with all the unique urls that were crawled in sorted manner.

**Note** - based on OS there can be a small delay until the file appears in system.

# Discussion
## System Design
![High Level System Design](high_level_design-1.jpg)

## Design Prioritization:

### Main requiremnts i prioritized:
#### Efficiency
1. Multi threading - to assure a faster crawling proccess.
2. Using in memory efficient data structures like queue and sets.
# Validation
1. Robust Valid URL checks
2. Normalization and Domain to prevent duplicants and infinite loops.
# Supporting future scalability
1. Using multi threads - so we can scale the system without much work.
2. Relevant class structures to support future enhancements (add priorities to specific url withing spider class, filtering with Web parse class etc')

### Main requiremnts i did not prioritize and why:
#### DataBase
1. Implementation of robust DB is relatively simple and the magnitude of storage is small so i chose to give this low priority.
2. Crash consitency - since program is relatively fast and implemeting a clever solution with multi threads will take a lot more time.
# Politeness
1. Each website has it's own requiremnts and it will take time to contruct something robust for all websites.
2. There was not clear instruction to take this into account and it is a field im not well familiar with so i skipped it.

### Components Deep Dive

#### 1. Client
- **Function**: Initiates the crawling process by providing the seed URL as input from user.

#### 2. URL Frontier
- **Responsibility**: Main program - manages spiders (threads) 
  - communication with all componants
  - Managing the databases of crawled/waiting urls.
- **Bottlenecks**:
  - currently not supporting websites policies (Politeness/robot.txt)
  - not supporting prioritization of specific urls
  - limited to # of threads by the single server running it.
- **Enhancements**:
  - **Politeness Policy**: Ensures the crawler does not overwhelm any server by following robot.txt rules - use proxy.
  - **Priority Queueing**: Uses a multi-level feedback queue (MLFQ) to prioritize URLs, in each level use Round Robin algorithm.
  - **Load Balancer**: a very important componant to add - will be reponsible for making sure no single thread/spider takes too many tasks,
    while other spiders remain unemployed

#### 3. Web Parser
- **Responsibility**: Fetche/Extract the HTML content of URLs from the internet.
- **Supporting Components**:
  - **DNS Lookup**: Resolves domain names - implemented by python
  - **Normalization**: Makes sure each url is converted to normalized form to assure each url points to exactly one page.
  - **Validation**: checks url is of valid form
  - **Fetch/Extract**: implements extract and fetch operation of spider class.
- **Bottlenecks**:
  - Parsing and normalization process can be computationally intensive.
  - Repetitive content fetching without cache utilization leads to inefficiencies.
  - DNS lookups can be slow and impact crawler performance.
  - Reliance on external Internet speed and stability.
- **Enhancements**:
  - Use a local caching DNS resolver to speed up domain name resolution.
  - Optimize network configurations and possibly use a dedicated Internet connection

#### 4. Spider (Crawlers)
- **Responsibility**: A class that performs the actual task of crawling by fetching pages and parsing HTML content.
- **Supporting Components**:
  - **Duplicants handler**: Avoide proccessing already crawled urls
- **Bottlenecks**:
  - As threads increase, the overhead of context switching can impact performance.
  - Managing a large number of threads efficiently is challenging (Locks mechanism slows perforamnce, user signals not currently supported)
  - Each duplicants handle implies searching for url in set.
- **Enhancements**:
  - Thread Pooling mechanism
  - Lock-Free Mechanism to minimize critical sections
  - Duplicants resolution - Use caching and LRU algorithm to avoid searching each url in set repeatedly.

 #### 5. Local Storage
- **Responsibility**: Store crawled data into a file and provide file operations methods.
- **Bottlenecks**:
  - I/O operations can slow down the system, especially when dealing with large amounts of data.
  - Crash Consistency - not supported currently when dealing with abrupt termination.
  - Limited storage - using memory based database (set , queue)
- **Enhancements**:
  - Use a more robust database system like PostgreSQL or MongoDB for storage.
  - Implement asynchronous I/O operations to enhance performance.

## Scalability 
The system is designed to scale across multiple servers with regard to the following requirements:
- **Distributed Crawling**: The architecture supports distributing tasks across multiple crawling instances (spiders), using shared resources like URL databases and caches.
- **Priority**: Prioritize in URL_Frontier which urls to crawl based on relevant factors like - Counter of times we tried to access url , specific domains etc'
- **Load Balancing**: We will need to implement a mechanism that ensures that all servers are given similar amount of work and that URLs to crawl are spreaded equally. this can be implemeted as a load balancer for example that uses Round Robin algorithm.
- **Cache**: To prevent different servers crawling the same pages we can use the LRU algorithm and a url cache to ensure that if different servers get the task to crawl the same page that was already crawled they can just take it from a shared cache to extract relevant data from it.
- **Capacity Estimates**: Given the amount of web pages we need to crawl we can calculate how much time it will take us to complete the task with how many servers available while also taking in acount website policies.
simple example: Crawling 1 Bilion pages given that each page is 1MB to store. we will need 1 Bilion requests and 1PB memory space. if we want to complete the assingment in 1 week (600K seconds) we need 1B/600k = 1500 requests per second. in general home wifi it takes 0.5 second to load a webpage thus 750 threads per second and we can calculate how many CPUs we need for that.

## Conclusions 
The project demonstrates a fast and efficient simple way to crawl the entire seed url while validating main requirements hold.
For the future there is a need to focus on Politeness , Distribution and more robust DataBase usage.

