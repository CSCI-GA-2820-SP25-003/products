$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#product_id").val(res.id);
        $("#product_sku").val(res.sku);
        $("#product_name").val(res.name);
        $("#product_description").val(res.description);
        $("#product_price").val(res.price);
        $("#product_image_url").val(res.image_url);
        $("#product_created_time").val(res.created_time);
        $("#product_updated_time").val(res.updated_time);
        $("#product_likes").val(res.likes);
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#product_sku").val("");
        $("#product_name").val("");
        $("#product_description").val("");
        $("#product_price").val("");
        $("#product_image_url").val("");
        $("#product_created_time").val("");
        $("#product_updated_time").val("");
        $("#product_likes").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create a Product
    // ****************************************

    $("#create-btn").click(function () {

        let sku = $("#product_sku").val();
        let name = $("#product_name").val();
        let description = $("#product_description").val();
        let price = $("#product_price").val();
        let image_url = $("#product_image_url").val();
        let likes = $("#product_likes").val();

        let data = {
            "sku": sku,
            "name": name,
            "description": description,
            "price": parseFloat(price),
            "image_url": image_url,
            "likes": parseInt(likes)
        };

        $("#flash_message").empty();
        
        let ajax = $.ajax({
            type: "POST",
            url: "/products",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Update a Product
    // ****************************************

    $("#update-btn").click(function () {

        let product_id = $("#product_id").val();
        let sku = $("#product_sku").val();
        let name = $("#product_name").val();
        let description = $("#product_description").val();
        let price = $("#product_price").val();
        let image_url = $("#product_image_url").val();
        let likes = $("#product_likes").val();

        let data = {
            "sku": sku,
            "name": name,
            "description": description,
            "price": parseFloat(price),
            "image_url": image_url,
            "likes": parseInt(likes)
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
                type: "PUT",
                url: `/products/${product_id}`,
                contentType: "application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Retrieve a Product
    // ****************************************

    $("#retrieve-btn").click(function () {

        let product_id = $("#product_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/products/${product_id}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Delete a Product
    // ****************************************

    $("#delete-btn").click(function () {

        let product_id = $("#product_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `/products/${product_id}`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Product has been Deleted!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#product_id").val("");
        $("#flash_message").empty();
        clear_form_data()
    });

    // ****************************************
    // Search for a Product
    // ****************************************

    $("#search-btn").click(function () {
        let name = $("#product_name").val();
        let sku = $("#product_sku").val();
        let min_price = $("#product_min_price").val();
        let max_price = $("#product_max_price").val();
    
        let queryString = "";
    
        // Add parameters to query string as needed
        if (sku) {
            queryString += 'sku=' + sku;
        }
        
        if (name) {
            if (queryString.length > 0) {
                queryString += '&';
            }
            queryString += 'name=' + name;
        }
        
        if (min_price) {
            if (queryString.length > 0) {
                queryString += '&';
            }
            queryString += 'min_price=' + min_price;
        }
        
        if (max_price) {
            if (queryString.length > 0) {
                queryString += '&';
            }
            queryString += 'max_price=' + max_price;
        }
    
        $("#flash_message").empty();
    
        let ajax = $.ajax({
            type: "GET",
            url: `/products?${queryString}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            $("#search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-1">ID</th>'
            table += '<th class="col-md-2">SKU</th>'
            table += '<th class="col-md-2">Name</th>'
            table += '<th class="col-md-3">Description</th>'
            table += '<th class="col-md-1">Price</th>'
            table += '<th class="col-md-2">Image URL</th>'
            table += '<th class="col-md-2">Created</th>'
            table += '<th class="col-md-2">Updated</th>'
            table += '<th class="col-md-1">Likes</th>'
            table += '</tr></thead><tbody>'
            let firstProduct = "";
            for(let i = 0; i < res.length; i++) {
                let product = res[i];
                table += `<tr id="row_${i}"><td>${product.id}</td><td>${product.sku}</td><td>${product.name}</td><td>${product.description}</td><td>${product.price}</td><td>${product.image_url}</td><td>${product.created_time}</td><td>${product.updated_time}</td><td>${product.likes}</td></tr>`;
                if (i == 0) {
                    firstProduct = product;
                }
            }
            table += '</tbody></table>';
            $("#search_results").append(table);

            // copy the first result to the form
            if (firstProduct != "") {
                update_form_data(firstProduct)
            }

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

})