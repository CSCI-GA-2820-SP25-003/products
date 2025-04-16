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
                table += `<tr id="row_${i}" onclick="openProduct()"><td>${product.id}</td><td>${product.sku}</td><td>${product.name}</td><td>${product.description}</td><td>${product.price}</td><td>${product.image_url}</td><td>${product.created_time}</td><td>${product.updated_time}</td><td>${product.likes}</td></tr>`;
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

    // create modal
    let overlay = document.createElement("div");
    overlay.id = "overlay";
    overlay.style.position = "fixed";
    overlay.style.top = "0";
    overlay.style.left = "0";
    overlay.style.right = "0";
    overlay.style.bottom = "0";
    overlay.style.display = "none";
    overlay.style.justifyContent = "center";
    overlay.style.alignItems = "center";
    overlay.style.backgroundColor = "rgba(0, 0, 0, 0.5)";

    let modal = document.createElement("div");
    modal.classList.add("well");
    modal.classList.add("col-md-8");

    let close_button = document.createElement("span");
    close_button.id = "modal_close-btn";
    close_button.classList.add("glyphicon");
    close_button.classList.add("glyphicon-remove");
    close_button.style.float = "right";
    close_button.style.paddingBottom = "10px";
    close_button.style.cursor = "pointer";
    close_button.style.color = "red";
    close_button.style.transform = "scale(1.5)";
    close_button.style.padding = "10px";
    close_button.style.paddingLeft = "15px";
    close_button.onclick = function() {
        overlay.style.display = "none";
    }

    let modal_retrieve_button = document.createElement("button");
    modal_retrieve_button.classList.add("btn");
    modal_retrieve_button.classList.add("btn-primary");
    modal_retrieve_button.style.float = "right";
    modal_retrieve_button.innerText = "Retrieve";
    modal_retrieve_button.id = "modal_retrieve-btn";

    let row = document.createElement("div");
    row.classList.add("row");

    let img_div = document.createElement("div");
    img_div.classList.add("col-md-4");

    let img = document.createElement("img");
    img.id = "modal_img";
    img.style.width = "100%";
    img.style.height = "auto";
    img.style.padding = "10px";
    img.style.paddingTop = "25px";
    img.alt = "Product Image";
    img_div.appendChild(img);

    let table = document.createElement("table");
    table.classList.add("col-md-8");
    table.classList.add("modal-table");

    let tbody = document.createElement("tbody");

    tbody.innerHTML += `<tr><td><b>ID</b></td><td id="modal_id"></td>`
    tbody.innerHTML += `<tr><td><b>SKU</b></td><td id="modal_sku"></td>`
    tbody.innerHTML += `<tr><td><b>Name</b></td><td id="modal_name"></td>`
    tbody.innerHTML += `<tr><td><b>Description</b></td><td id="modal_description"></td>`
    tbody.innerHTML += `<tr><td><b>Price</b></td><td id="modal_price"></td>`
    tbody.innerHTML += `<tr><td><b>Image URL</b></td><td id="modal_image_url"></td>`
    tbody.innerHTML += `<tr><td><b>Created</b></td><td id="modal_created"></td>`
    tbody.innerHTML += `<tr><td><b>Updated</b></td><td id="modal_updated"></td>`
    tbody.innerHTML += `<tr><td><b>Likes</b></td><td id="modal_likes"></td>`

    table.appendChild(tbody);

    modal.appendChild(close_button);
    modal.appendChild(modal_retrieve_button);

    row.appendChild(img_div);
    row.appendChild(table);
    modal.appendChild(row);

    overlay.appendChild(modal);
    $(".container").append(overlay);

    $("#modal_retrieve-btn").click(function () {
        let product_id = $("#modal_id").text();
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

        overlay.style.display = "none";
    });
})

// onclick tr event
function openProduct() {
    var e = event.target;

    if (e.tagName === "TD") {
        e = e.parentNode;
    }

    let tds = e.children;
    tds = Array.from(tds);

    $("#modal_id").text(tds[0].innerText);
    $("#modal_sku").text(tds[1].innerText);
    $("#modal_name").text(tds[2].innerText);
    $("#modal_description").text(tds[3].innerText);
    $("#modal_price").text(tds[4].innerText);
    $("#modal_image_url").text(tds[5].innerText);
    $("#modal_created").text(tds[6].innerText);
    $("#modal_updated").text(tds[7].innerText);
    $("#modal_likes").text(tds[8].innerText);

    $("#modal_img").attr("src", tds[5].innerText);

    $("#overlay").css("display", "flex");
}
