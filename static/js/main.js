
$(document).ready(function() {

    $('#editBtn').on('click', function() {
        const aiText = $('#aiResponse').text().trim();
        if (aiText.length > 0) {
            let currentText = $('#userText').val();
           
            if (!currentText.endsWith(aiText)) {
                if (currentText.length > 0 && !currentText.endsWith('\n')) {
                    currentText += '\n';
                }
                $('#userText').val(currentText + aiText);
            }
           
            $('#responseSection').hide();
            $('#aiResponse').text('');
           
            $('#userText').focus();
        }
    });
   
    let currentAIResponse = '';
    let currentUserText = '';
    let currentPersonality = '';
    
    function validateForm() {
        let isValid = true;
        const title = $('#storyTitle').val().trim();
        const text = $('#userText').val().trim();
        
        if (title.length < 3) {
            $('#storyTitle').addClass('is-invalid');
            isValid = false;
        } else {
            $('#storyTitle').removeClass('is-invalid');
        }
        
        if (text.length < 20) {
            $('#userText').addClass('is-invalid');
            isValid = false;
        } else {
            $('#userText').removeClass('is-invalid');
        }
        
        return isValid;
    }
    
    $('#storyForm').on('submit', function(e) {
        e.preventDefault();
        
        if (!validateForm()) {
            return;
        }
        
        currentUserText = $('#userText').val().trim();
        currentPersonality = $('#personality').val();
        
        $('#loadingSpinner').show();
        $('#responseSection').hide();
        $('#generateBtn').prop('disabled', true);
        
        $.ajax({
            url: '/generate',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                user_text: currentUserText,
                personality: currentPersonality
            }),
            success: function(response) {
                currentAIResponse = response.ai_response;
                $('#aiResponse').text(currentAIResponse);
                $('#responseSection').fadeIn();
                $('#loadingSpinner').hide();
                $('#generateBtn').prop('disabled', false);
            },
            error: function(xhr) {
                $('#errorMessage').text(xhr.responseJSON?.error || 'Failed to generate story');
                $('#errorAlert').show();
                $('#loadingSpinner').hide();
                $('#generateBtn').prop('disabled', false);
            }
        });
    });
    
    $('#regenerateBtn').on('click', function() {
        $('#storyForm').submit();
    });
    
    $('#saveBtn').on('click', function() {
        const title = $('#storyTitle').val().trim();
        const userText = $('#userText').val().trim();
        const aiResponse = currentAIResponse;
        const personality = $('#personality').val();

        if (title.length < 3 || userText.length < 20 || !aiResponse) {
            $('#errorMessage').text('Please provide a valid title, story text, and generate a story before saving.');
            $('#errorAlert').show();
            return;
        }

        $('#saveBtn').prop('disabled', true);
        $('#saveSpinner').show();
        $('#errorAlert').hide();
        $('#successAlert').hide();

        $.ajax({
            url: '/save',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                title: title,
                user_text: userText,
                ai_response: aiResponse,
                personality: personality
            }),
            success: function(response) {
                $('#successMessage').text('Story saved successfully!');
                $('#successAlert').show();
                $('#saveBtn').prop('disabled', false);
                $('#saveSpinner').hide();
            },
            error: function(xhr) {
                $('#errorMessage').text(xhr.responseJSON?.error || 'Failed to save story');
                $('#errorAlert').show();
                $('#saveBtn').prop('disabled', false);
                $('#saveSpinner').hide();
            }
        });
    });

    $('#storyTitle, #userText').on('input', function() {
        $('#errorAlert').hide();
        $('#successAlert').hide();
    });

    $('#closeErrorAlert').on('click', function() {
        $('#errorAlert').hide();
    });

    $('#closeSuccessAlert').on('click', function() {
        $('#successAlert').hide();
    });

    // Clear button handler
    $('#clearBtn').on('click', function() {
       
        $('#storyTitle').val('');
        $('#userText').val('');
        $('#personality').prop('selectedIndex', 0);
        
        $('#storyTitle').removeClass('is-invalid');
        $('#userText').removeClass('is-invalid');
        
        $('#errorAlert').hide();
        $('#successAlert').hide();
        $('#aiResponse').text('');
        $('#responseSection').hide();
    });

});