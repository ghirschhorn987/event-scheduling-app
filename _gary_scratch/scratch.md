I want to update authentication.md doc.  

1. The User Roles section is wrong.  It shoud indicate that the basic User object and information is the same for all users.  What the system uses to distinguish user privileges and capabilities is a User Group mechansim where a User can belong to zero or more User Groups.

Initially, we have these User Groups although more may be added in future:
- SuperAdmin:  has full unrestricted access to all part of the system
- Admin:  initially, same access as SuperAdmin but might change in future
- FirstPriority: used by certain system functionality to determine order among users - grants first priority
- SecondaryPriority: used by certain system functionaly to determine order among users - grants second priority
- BethAmAffiliated - notes those users who have an affiliation with Beth Am

2. 


