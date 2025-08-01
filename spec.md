Project Specs Doc Requirment



Global utils
	1. Response structure : {
				status : 200,
				data : {token : string} # User information,
				message : ""
			}

Requirement : 

1. Purpose: I want to design the library management backend server.


2. Dependencies : 
Backend Framework
Django 5.2+: Web framework
Django REST Framework: API development
djangorestframework-simplejwt: JWT authentication
Database
PostgreSQL: Primary database with ACID compliance
Docker: Database containerization
Additional Components
Custom Exception Handling: Centralized error management
Logging System: Application monitoring and debugging
Environment Configuration: Development/Production separation
API Documentation: drf-yasg or drf-spectacular
Deployment Architecture


3. Data Models : 

	a. User Model: User model should contain the id, name, role, is_active, permisssion_groups (that should be false by default, and other nessasary fields.
	b. Book Model: My book model should contain the id,title, author, publisher, publication, genre, language, quantity  and description of the book.
	c. BorrowRecord Model: that model should contain like user id, book id, borrow_status it's own book id.
	d. Permission module: So there should be permission group for user and admin, where we can create the set of permission first, with fields like id, name, and other remaining fields. and there should be another models for the permission group that contain set of permissions, and admin can assign the group to the user.

NOTE : Each model should has created_by, updated_by, created_on, updated_on in each model data row.

API Endpoints

Endpoint Paths and HTTP Methods: List all API endpoints, their corresponding HTTP methods (GET, POST, PUT, DELETE), and URL paths.
    
    
    USER API ENDPOINTS
	a. USER APIs : all the user related api should be start with /auth/. 
	b. API Endpoints:
		1. BASE_URL/auth
			a. request body : {
				 name:string,
				 role:string "user | admin", 
				 is_active : boolean (default false), 
				 permisssion_groups : string[],
				 email:string,
				 password : string
			}
			b. Response body : {
				status : 201,
				data : {} # User information,
				message : ""
			}
			c. Method : POST
		2. BASE_URL/auth/login
			a. request body : {
				email : string,
				password : string 
			}
			b. Response body : {
				status : 200,
				data : {token : string} # User information,
				message : ""
			}
			c. Method : POST
		3. BASE_URL/auth
			a. method : patch
		4. BASE_URL/auth
			a. method : delete

    BOOK MODEL ENDPOINTS
    	a. BASE_URL/books
    		a. request body : {
    			title:string , 
    			author:string, 
    			publisher:string, 
    			publication:string, 
    			genre:sting, 
    			language:string, 
    			quantity:int,
    			description:string
    		}
    		Response : follow the global response structure.
    		b. method : POST
    	b. BASE_URL/book/?
    		a. request query : {
    			title?:string , 
    			author?:string, 
    			publisher?:string, 
    			publication?:string, 
    			genre?:sting, 
    			language?:string, 
    		}
    		b. response : It should follow the global response structure.
    		c. method : GET
			

Note : Other endpoits like patch and delete should get required information that is needed.

	b. Authentication and Authorization: Create the middle where that will validate the user JWT and the expiry of the token.
	c. Error Handling: Once any API is falied response proper response with respective response structure.



Services and Business Logic : 