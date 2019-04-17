\
Foundation Principles
=====================

The foundation principles are the principles that must be followed at all the times.  The principles are:
1. Dell EMC Principle
2. OA-AO Principle
3. Ease of Use Principle
4. Repeatable Principle
5. Consistency Principle
6. SPORTS Principle

# Dell EMC Principle
APIs must always be consistent with Dell EMC Systems Management Strategy and Best Practices of the relevant Product lines.

# OA-AO (One API for An Operation) Principle
An Operation is a task, job or action that results in a desired end state of the system.
1. Do not create multiple APIs for the same operation.
2. Do not combine two independent tasks into an API (for example, do not combine Server Configuration and Operating System Deployment into one API)
3. For operations taking long time, the API must allow for both synchronous and asynchronous options.
    1.  In synchronous case, the API will wait till the operation completes
    2.  In case of asynchronous case, the API will return immediately with an handle. The user can poll for status using that handle.
    3.  A variant of asynchronous option is to allow the user to specify a callback.
    4.  Have an timeout variable.  The API must exit when that timeout occurs. Timeout should be the maximum time that the API will wait altogether in that API (including all loops, waits, retries and internal timeouts). This definition brings confidence to API users that the API will not take more than a fixed time.
    5.  When a timeout occurs, return failure from the API.
4. Keep all the APIs modular
5. APIs must be transparent to protocol and other internals. 
    1. Remember, the user intent is to perform an action with your system. The user intent is not to achieve the same via a specific protocol
    2. Protocols just provide you a way to achieve that operation. Just because the system supports multiple protocols, it does not mean you should expose that to user.
    3. Sometimes a user may want to control the protocol. Provide the users with a concept on preferences - so that users can specify their own protocol choice if they want.
    4. Design should always assume that users first choice is to do it Dell's way.
    5. Design should also assume that user may want to try all feasible ways to execute the action as is possible.

# Ease of Use Principle
1. APIs should be easy to use.
    1. Ease of use is from user point of view.
    2. If it becomes easier for you if user passes the same parameters multiple times, that is not ease of use.  You should provide a way to encapsuate those parameters in a structure.
    3. Return as much information as possible to user.  Leave him to make the choice
    4. Use simpler and well known datastructures.  Don't create you own variant of datastructures.  For example, OMSDK uses JSONs everywhere
    5. Use language constructs to make the life of user easy
    6. User should be able to catch logical errors as early as possible. Use language constructs as much as possible. Example: OMSDK typemgr code
2. APIs must hide complexity and tribal knowledge.  Example: Liason Share and Update Share simplify configuration and update use cases

# Repeatability Principle
Repeatablility means the ability to call the same API multiple times, resulting in the same end state of the system.
1. All APIs that treat multiple entities (users, NICs, Virtual Drives) when called twice should not create duplicate instances.
2. An API called twice should not result in different state of the system.  For example, calling "Clear Config" any number of times should result in the same behavior: the configuration is cleared

# Consistency Principle
Consistency is the conformity to standard principles all the time.
1. APIs must be consistent in naming - function names, API arguments, enumerations etc.
2. APIs belonging to similar function must be consistent in return values - 
3. APIs must be consistent with CRUD and ACID principles.
4. APIs must cover well-rounded use cases.  Don't just add a Create API.  Instead add a Create, Modify, Delete and List APIs.  If an API is irrelevant, simply make it as not_implemented.
5. APIs must use consistent arguments for the APIs.
     1. For example, if parameters are passed as individual arguments to Create function, they should be passed as individual arguments to list, modify and delete functions
     2. On the other hand, if you pass a structure, you should pass a structure to all.

# SPORTS Principle
SPORTS is an acronym for Simple, Portable, Optimal, Reliable, Transparent and Scalable
1. APIs must be simple. APIs must hide complexity and tribal knowledge from the consumer.
2. APIs must be transparent to the platform on which it is executed.
    1.  Avoid C/C++/Native or Platform dependent code.
    2. If you have plan to write a python wrapper on a C-based tool, how would you support custom Linux installations? Your C-based tool need to be also supported for those Linux Installations as well - is that feasible.
    3. Instead go with pure-python implementation.
    4. In that case, as long as python community supports the python in that custom installation, we are good. 
3. API implementations must be written optimally.  Don't write voluminous code which can be written in fewer lines
3. APIs must use only reliable dependencies - stable and supported dependent components
4. APIs must be transparent to the protocol being used
5. APIs must be thread-safe and scalable
6. APIs should not allow user to specify parameters if it does not make sense.


