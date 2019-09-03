echo "**********************************"
echo "Removing old yarn.lock files, we use npm..."
echo "**********************************"

cd frontend; 
  for OUTPUT in $(ls -d node_modules/*/)
    do
      if [[ $OUTPUT == *"node_modules"* ]]; then
          cd $OUTPUT
          echo "Removing old Yarn Locks. $(basename $(pwd))"
          rm -rf yarn.lock;
          cd ../..
      fi
done
