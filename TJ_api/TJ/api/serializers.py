from rest_framework import serializers
from .models import Address, Department, Job, User, PerformanceReview


class AddressSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'url', 'street', 'city', 'state', 'postal_code', 'country']


class DepartmentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'url', 'name']


class JobSerializer(serializers.HyperlinkedModelSerializer):
    department_id = serializers.HyperlinkedRelatedField(view_name='department-detail', queryset=Department.objects.all())

    class Meta:
        model = Job
        fields = ['id', 'url', 'job_title', 'job_description', 'department_id']


class UserSerializer(serializers.HyperlinkedModelSerializer):
    address = AddressSerializer()
    job_id = JobSerializer()

    class Meta:
        model = User
        fields = [
            'id', 'url', 'first_name', 'last_name', 'address', 'phone_number',
            'email', 'role', 'date_of_hire', 'job_id'
        ]

    def create(self, validated_data):
        address_data = validated_data.pop('address')
        job_data = validated_data.pop('job_id')

        address = Address.objects.create(**address_data)
        job = Job.objects.create(**job_data)

        user = User.objects.create(address=address, job_id=job, **validated_data)
        return user

    def update(self, instance, validated_data):
        address_data = validated_data.pop('address', None)
        job_data = validated_data.pop('job_id', None)

        if address_data:
            for field, value in address_data.items():
                setattr(instance.address, field, value)
            instance.address.save()

        if job_data:
            for field, value in job_data.items():
                setattr(instance.job_id, field, value)
            instance.job_id.save()

        for field, value in validated_data.items():
            setattr(instance, field, value)

        instance.save()
        return instance


class PerformanceReviewSerializer(serializers.HyperlinkedModelSerializer):
    employee = serializers.HyperlinkedRelatedField(view_name='user-detail', queryset=User.objects.all())
    rater = serializers.HyperlinkedRelatedField(view_name='user-detail', queryset=User.objects.all())

    class Meta:
        model = PerformanceReview
        fields = ['id', 'url', 'employee', 'rater', 'score', 'comment', 'review_date']

    def validate(self, data):
        employee = data['employee']
        rater = data['rater']

        # Ensure both employee and rater have the employee role
        if employee.role != User.RoleType.EMPLOYEE:
            raise serializers.ValidationError('The person being rated must have the employee role.')
        if rater.role != User.RoleType.EMPLOYEE:
            raise serializers.ValidationError('The rater must have the employee role.')

        # Ensure the rater has not already rated this employee
        if PerformanceReview.objects.filter(employee=employee, rater=rater).exists():
            raise serializers.ValidationError('You have already rated this employee.')

        return data
